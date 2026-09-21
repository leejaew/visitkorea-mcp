import express, { type Express, type Request, type Response, type NextFunction } from "express";
import cors from "cors";
import helmet from "helmet";
import rateLimit from "express-rate-limit";
import pinoHttp from "pino-http";
import { createProxyMiddleware } from "http-proxy-middleware";
import router from "./routes";
import { logger } from "./lib/logger";

export type AppOptions = {
  pythonTarget: string;
  pythonReady: Promise<void>;
};

function validatePythonTarget(pythonTarget: string): URL {
  const target = new URL(pythonTarget);
  const port = Number(target.port);
  if (
    target.protocol !== "http:" ||
    target.hostname !== "127.0.0.1" ||
    !Number.isInteger(port) ||
    port < 1 ||
    port > 65535 ||
    target.pathname !== "/" ||
    target.search ||
    target.hash
  ) {
    throw new Error("Python target must be an HTTP URL on 127.0.0.1 with a valid port");
  }
  return target;
}

/**
 * Poll the Python MCP server's /healthz endpoint until it returns HTTP 200.
 * This is deliberately called by the process entry point, not while this
 * module is imported or while an app is being constructed.
 */
export async function waitForPythonHttp(
  pythonTarget: string,
  maxWaitMs = 300_000,
): Promise<void> {
  const target = validatePythonTarget(pythonTarget);
  const url = new URL("/healthz", target).toString();
  const port = target.port;
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

export function createApp({ pythonTarget, pythonReady }: AppOptions): Express {
  validatePythonTarget(pythonTarget);
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
          return { statusCode: res.statusCode };
        },
      },
    }),
  );

  // CORS — intentionally open for a public MCP server
  app.use(cors());

  // Rate limiter for the MCP proxy — protects upstream KTO API quota
  const mcpLimiter = rateLimit({
    windowMs: 60 * 1000,
    max: 120,
    standardHeaders: true,
    legacyHeaders: false,
    message: { error: "Too many requests. Please slow down." },
    skip: (req) => req.ip === "127.0.0.1" || req.ip === "::1",
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
      target: pythonTarget,
      changeOrigin: false,
      pathRewrite: { "^/": "/mcp" },
      proxyTimeout: 35_000,
      timeout: 35_000,
    }),
  );

  app.use(express.json());
  app.use(express.urlencoded({ extended: true }));
  app.use("/api", router);
  return app;
}
