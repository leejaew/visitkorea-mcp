import express, { type Express, type Request, type Response, type NextFunction } from "express";
import cors from "cors";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
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

// Security headers — disable CSP and COEP since this is an API/proxy server
app.use(
  helmet({
    contentSecurityPolicy: false,
    crossOriginEmbedderPolicy: false,
  }),
);

app.use(
  pinoHttp({
    logger,
    serializers: {
      req(req) {
        return {
          id: req.id,
          method: req.method,
          url: req.url?.split("?")[0], // strip query string to avoid logging API keys
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

// CORS — intentionally open for a public MCP server
app.use(cors());

// Rate limiter for the MCP proxy — protects upstream KTO API quota
const mcpLimiter = rateLimit({
  windowMs: 60 * 1000,   // 1 minute window
  max: 120,              // 120 requests per IP per minute (~2 req/s burst)
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: "Too many requests. Please slow down." },
  skip: (req) => req.ip === "127.0.0.1" || req.ip === "::1", // skip loopback
});

const waitForPython = async (_req: Request, res: Response, next: NextFunction) => {
  try {
    await pythonReady;
    next();
  } catch {
    res.status(503).json({ error: "MCP server unavailable" });
  }
};

// Streamable HTTP transport — MCP endpoint for Claude AI and other HTTP-based clients
app.use("/mcp", mcpLimiter);
app.use("/mcp", waitForPython);
app.use(
  "/mcp",
  createProxyMiddleware({
    target: "http://127.0.0.1:3001", // loopback only — Python binds 127.0.0.1
    changeOrigin: false,
    pathRewrite: { "^/": "/mcp" },
    proxyTimeout: 35_000, // slightly above Python's 30 s httpx timeout
    timeout: 35_000,
  }),
);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/api", router);

export default app;
