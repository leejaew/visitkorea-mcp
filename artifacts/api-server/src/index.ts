import { spawn } from "child_process";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { createApp, waitForPythonHttp } from "./app";
import { logger } from "./lib/logger";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const workspaceRoot = path.resolve(__dirname, "../../..");
const serverScript = path.join(workspaceRoot, "visitkorea-mcp/main.py");

const dotPylibsPython = path.join(workspaceRoot, ".pythonlibs/bin/python3.11");
const pythonExe = fs.existsSync(dotPylibsPython) ? dotPylibsPython : "python3.11";

function parsePort(name: string, raw: string | undefined, fallback?: number): number {
  const value = raw ?? (fallback === undefined ? undefined : String(fallback));
  const port = value === undefined ? NaN : Number(value);
  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error(`Invalid ${name} value: "${value ?? ""}" (expected 1-65535)`);
  }
  return port;
}

const publicPort = parsePort("PORT", process.env["PORT"]);
const pythonPort = parsePort("PYTHON_PORT", process.env["PYTHON_PORT"], 3001);
const pythonTarget = `http://127.0.0.1:${pythonPort}`;

function spawnPython(executable: string) {
  return spawn(executable, [serverScript, "--http", "--port", String(pythonPort)], {
    cwd: workspaceRoot,
    env: process.env,
    stdio: "inherit",
  });
}

async function startPython() {
  logger.info({ pythonExe, pythonPort }, "Starting Python MCP server");
  const child = spawnPython(pythonExe);
  try {
    await new Promise<void>((resolve, reject) => {
      child.once("spawn", resolve);
      child.once("error", reject);
    });
    return child;
  } catch (err) {
    // spawn errors mean no child exists; retry only then, avoiding orphaned
    // fallback processes when the first process starts successfully.
    logger.warn({ err }, "Configured Python executable failed; trying python3");
    const fallback = spawnPython("python3");
    await new Promise<void>((resolve, reject) => {
      fallback.once("spawn", resolve);
      fallback.once("error", reject);
    });
    return fallback;
  }
}

const pythonServer = await startPython();
const app = createApp({
  pythonTarget,
  pythonReady: waitForPythonHttp(pythonTarget),
});

let shuttingDown = false;
let httpServer: ReturnType<typeof app.listen> | undefined;

function waitForPythonExit(): Promise<void> {
  if (pythonServer.exitCode !== null || pythonServer.signalCode !== null) {
    return Promise.resolve();
  }
  return new Promise((resolve) => pythonServer.once("exit", () => resolve()));
}

async function shutdown(signal: string, exitCode: number) {
  if (shuttingDown) return;
  shuttingDown = true;
  logger.info({ signal }, "Shutting down");

  // Start both operations before awaiting either one. An active HTTP request
  // must not prevent us from stopping the Python worker.
  const httpDrain = httpServer
    ? new Promise<void>((resolve) => httpServer?.close(() => resolve()))
    : Promise.resolve();
  const pythonStop = waitForPythonExit();
  if (pythonServer.exitCode === null && pythonServer.signalCode === null) {
    pythonServer.kill("SIGTERM");
  }

  const allStopped = Promise.all([httpDrain, pythonStop]);
  let timedOut = false;
  let deadline: ReturnType<typeof setTimeout> | undefined;
  await Promise.race([
    allStopped,
    new Promise<void>((resolve) => {
      deadline = setTimeout(() => {
        timedOut = true;
        resolve();
      }, 5_000);
    }),
  ]);
  if (deadline) clearTimeout(deadline);

  // closeAllConnections releases keep-alive and in-flight sockets that
  // prevented server.close from completing. Escalate Python only if it did
  // not honor SIGTERM within the same bounded window.
  if (timedOut && httpServer) httpServer.closeAllConnections();
  if (timedOut && pythonServer.exitCode === null && pythonServer.signalCode === null) {
    pythonServer.kill("SIGKILL");
  }
  await Promise.race([
    allStopped,
    new Promise<void>((resolve) => setTimeout(resolve, 1_000)),
  ]);
  process.exitCode = exitCode;
}

pythonServer.on("exit", (code, signal) => {
  logger.warn({ code, signal }, "Python MCP server exited");
  if (!shuttingDown) {
    void shutdown("python-exit", 1).then(() => process.exit(1));
  }
});

httpServer = app.listen(publicPort, () => logger.info({ port: publicPort }, "Server listening"));

// The child can exit between startPython() resolving and the exit listener
// being attached. Check its state after the listener is assigned as well.
if (pythonServer.exitCode !== null || pythonServer.signalCode !== null) {
  void shutdown("python-exit", 1).then(() => process.exit(1));
}

process.once("SIGTERM", () => void shutdown("SIGTERM", 0).then(() => process.exit(0)));
process.once("SIGINT", () => void shutdown("SIGINT", 0).then(() => process.exit(0)));
