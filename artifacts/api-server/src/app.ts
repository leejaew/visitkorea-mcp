import express, { type Express, type Request, type Response, type NextFunction } from "express";
import cors from "cors";
import pinoHttp from "pino-http";
import { createProxyMiddleware } from "http-proxy-middleware";
import router from "./routes";
import { logger } from "./lib/logger";

/**
 * Poll the Python MCP server's /healthz endpoint until it returns HTTP 200.
 * This guarantees the session manager lifespan has started (the task group is
 * initialised) before we forward any MCP traffic.  A plain TCP-port check
 * resolves too early — the port opens before Starlette's lifespan runs.
 */
async function waitForPythonHttp(port: number, maxWaitMs = 300_000): Promise<void> {
  const url = `http://127.0.0.1:${port}/healthz`;
  const start = Date.now();
  while (Date.now() - start < maxWaitMs) {
    try {
      const res = await fetch(url);
      if (res.status === 200) {
        logger.info({ port }, "Python MCP server is ready");
        return;
      }
    } catch {
      // server not yet accepting connections — keep polling
    }
    await new Promise((r) => setTimeout(r, 1000));
  }
  throw new Error(`Timed out waiting for Python MCP server on port ${port}`);
}

const pythonReady = waitForPythonHttp(3001);

const app: Express = express();

app.use(
  pinoHttp({
    logger,
    serializers: {
      req(req) {
        return {
          id: req.id,
          method: req.method,
          url: req.url?.split("?")[0],
        };
      },
      res(res) {
        return {
          statusCode: res.statusCode,
        };
      },
    },
  }),
);
app.use(cors());

const waitForPython = async (_req: Request, res: Response, next: NextFunction) => {
  try {
    await pythonReady;
    next();
  } catch {
    res.status(503).json({ error: "MCP server unavailable" });
  }
};

// Streamable HTTP transport — MCP endpoint for Claude AI and other HTTP-based clients
app.use("/mcp", waitForPython);
app.use(
  "/mcp",
  createProxyMiddleware({
    target: "http://localhost:3001",
    changeOrigin: false,
    pathRewrite: { "^/": "/mcp" },
  }),
);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/api", router);

export default app;
