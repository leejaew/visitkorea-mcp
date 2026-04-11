import { spawn } from "child_process";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import app from "./app";
import { logger } from "./lib/logger";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const workspaceRoot = path.resolve(__dirname, "../../..");
const serverScript = path.join(workspaceRoot, "visitkorea-mcp/main.py");

const dotPylibsPython = path.join(workspaceRoot, ".pythonlibs/bin/python3.11");
const pythonExe = fs.existsSync(dotPylibsPython) ? dotPylibsPython : "python3.11";

logger.info({ pythonExe }, "Starting Python MCP server");

const pythonServer = spawn(pythonExe, [serverScript, "--http", "--port", "3001"], {
  cwd: workspaceRoot,
  env: process.env,
  stdio: "inherit",
});

pythonServer.on("error", (err) => {
  logger.error({ err }, "Failed to start Python MCP server — retrying with python3");
  const fallback = spawn("python3", [serverScript, "--http", "--port", "3001"], {
    cwd: workspaceRoot,
    env: process.env,
    stdio: "inherit",
  });
  fallback.on("error", (e) => logger.error({ err: e }, "Python3 fallback also failed"));
  fallback.on("exit", (code, signal) => logger.warn({ code, signal }, "Python3 fallback exited"));
  process.on("exit", () => fallback.kill());
});

pythonServer.on("exit", (code, signal) => {
  logger.warn({ code, signal }, "Python MCP server exited");
});

process.on("exit", () => {
  pythonServer.kill();
});

const rawPort = process.env["PORT"];

if (!rawPort) {
  throw new Error(
    "PORT environment variable is required but was not provided.",
  );
}

const port = Number(rawPort);

if (Number.isNaN(port) || port <= 0) {
  throw new Error(`Invalid PORT value: "${rawPort}"`);
}

app.listen(port, (err) => {
  if (err) {
    logger.error({ err }, "Error listening on port");
    process.exit(1);
  }

  logger.info({ port }, "Server listening");
});
