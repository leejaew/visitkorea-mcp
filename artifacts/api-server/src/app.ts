import net from "net";
import express, { type Express, type Request, type Response, type NextFunction } from "express";
import cors from "cors";
import pinoHttp from "pino-http";
import { createProxyMiddleware } from "http-proxy-middleware";
import router from "./routes";
import { logger } from "./lib/logger";

function waitForPort(port: number, maxWaitMs = 300_000): Promise<void> {
  return new Promise((resolve, reject) => {
    const start = Date.now();
    const attempt = () => {
      const socket = net.createConnection(port, "127.0.0.1");
      socket.on("connect", () => {
        socket.destroy();
        logger.info({ port }, "Python MCP server is ready");
        resolve();
      });
      socket.on("error", () => {
        socket.destroy();
        if (Date.now() - start < maxWaitMs) {
          setTimeout(attempt, 2000);
        } else {
          reject(new Error(`Timed out waiting for Python MCP server on port ${port}`));
        }
      });
    };
    attempt();
  });
}

const pythonReady = waitForPort(3001);

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

// Streamable HTTP transport — used by Claude AI (claude.ai) custom connector
app.use("/mcp", waitForPython);
app.use(
  "/mcp",
  createProxyMiddleware({
    target: "http://localhost:3001",
    changeOrigin: false,
    pathRewrite: { "^/": "/mcp" },
  }),
);

// SSE transport — default for Manus AI and other SSE-based MCP clients
app.use(["/sse", "/messages"], waitForPython);
app.use(
  ["/sse", "/messages"],
  createProxyMiddleware({
    target: "http://localhost:3001",
    changeOrigin: false,
    on: {
      proxyReq: (proxyReq) => {
        // Remove compression to keep SSE stream intact
        proxyReq.removeHeader("accept-encoding");
      },
    },
  }),
);

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/api", router);

export default app;
