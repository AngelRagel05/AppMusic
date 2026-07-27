"use strict";

const { execFile, spawn } = require("node:child_process");
const net = require("node:net");

const {
  createBackendSpawnConfiguration,
} = require("./runtimePaths");

function findFreePort(host = "127.0.0.1") {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.unref();
    server.once("error", reject);
    server.listen(0, host, () => {
      const address = server.address();
      const port = typeof address === "object" && address ? address.port : null;
      server.close((error) => {
        if (error) {
          reject(error);
        } else if (!port) {
          reject(new Error("No se pudo reservar un puerto local."));
        } else {
          resolve(port);
        }
      });
    });
  });
}

function delay(milliseconds) {
  return new Promise((resolve) => setTimeout(resolve, milliseconds));
}

async function waitForHttpEndpoint(
  url,
  {
    fetchImpl = globalThis.fetch,
    timeoutMs = 30_000,
    intervalMs = 250,
    validateResponse = (response) => response.ok,
    getStartupError = () => null,
  } = {},
) {
  const deadline = Date.now() + timeoutMs;
  let lastError = null;
  while (Date.now() < deadline) {
    const startupError = getStartupError();
    if (startupError) {
      throw startupError;
    }
    try {
      const response = await fetchImpl(url);
      if (await validateResponse(response)) {
        return;
      }
      lastError = new Error(`El endpoint respondio con HTTP ${response.status}.`);
    } catch (error) {
      lastError = error;
    }
    await delay(intervalMs);
  }

  const details = lastError instanceof Error ? ` ${lastError.message}` : "";
  throw new Error(`Tiempo agotado esperando ${url}.${details}`);
}

function waitForChildExit(childProcess, timeoutMs) {
  if (!childProcess || childProcess.exitCode !== null) {
    return Promise.resolve(true);
  }
  return new Promise((resolve) => {
    const timeout = setTimeout(() => {
      childProcess.removeListener("exit", onExit);
      resolve(false);
    }, timeoutMs);
    const onExit = () => {
      clearTimeout(timeout);
      resolve(true);
    };
    childProcess.once("exit", onExit);
  });
}

function killWindowsProcessTree(processId, execFileImpl = execFile) {
  return new Promise((resolve, reject) => {
    execFileImpl(
      "taskkill.exe",
      ["/PID", String(processId), "/T", "/F"],
      { windowsHide: true },
      (error) => {
        if (error && !["128", "255"].includes(String(error.code))) {
          reject(error);
        } else {
          resolve();
        }
      },
    );
  });
}

async function stopChildProcess(
  childProcess,
  {
    platform = process.platform,
    gracefulTimeoutMs = 8_000,
    execFileImpl = execFile,
  } = {},
) {
  if (!childProcess || childProcess.exitCode !== null) {
    return;
  }

  if (childProcess.stdin?.writable) {
    childProcess.stdin.write("shutdown\n");
  }
  if (await waitForChildExit(childProcess, gracefulTimeoutMs)) {
    return;
  }

  if (platform === "win32") {
    await killWindowsProcessTree(childProcess.pid, execFileImpl);
  } else {
    childProcess.kill("SIGKILL");
  }
  await waitForChildExit(childProcess, 2_000);
}

class BackendProcess {
  constructor({
    paths,
    logger,
    spawnImpl = spawn,
    fetchImpl = globalThis.fetch,
    onUnexpectedExit = () => {},
  }) {
    this.paths = paths;
    this.logger = logger;
    this.spawnImpl = spawnImpl;
    this.fetchImpl = fetchImpl;
    this.onUnexpectedExit = onUnexpectedExit;
    this.childProcess = null;
    this.port = null;
    this.baseUrl = null;
    this.isStopping = false;
    this.isReady = false;
    this.startupError = null;
    this.recentOutput = [];
  }

  async start() {
    if (this.childProcess) {
      throw new Error("El backend de SoundShelf ya esta iniciado.");
    }

    this.port = await findFreePort();
    this.baseUrl = `http://127.0.0.1:${this.port}`;
    const launch = createBackendSpawnConfiguration(this.paths, this.port);
    this.logger.info(
      `Iniciando backend en ${this.baseUrl} con ${launch.command}.`,
    );
    this.childProcess = this.spawnImpl(launch.command, launch.arguments, {
      ...launch.options,
      stdio: ["pipe", "pipe", "pipe"],
      windowsHide: true,
    });
    this.captureOutput(this.childProcess.stdout, "stdout");
    this.captureOutput(this.childProcess.stderr, "stderr");
    this.childProcess.once("error", (error) => {
      this.startupError = new Error(
        `No se pudo ejecutar el backend: ${error.message}`,
      );
    });
    this.childProcess.once("exit", (code, signal) => {
      const error = new Error(
        `El backend termino inesperadamente (codigo ${code}, señal ${signal || "ninguna"}).`,
      );
      if (!this.isStopping && this.isReady) {
        this.startupError = error;
        this.onUnexpectedExit(error);
      } else if (!this.isStopping) {
        this.startupError = error;
      }
    });

    try {
      await waitForHttpEndpoint(`${this.baseUrl}/api/health`, {
        fetchImpl: this.fetchImpl,
        timeoutMs: 45_000,
        validateResponse: async (response) => {
          if (!response.ok) {
            return false;
          }
          const body = await response.json();
          return body?.status === "ok";
        },
        getStartupError: () => this.startupError,
      });
    } catch (error) {
      await this.stop();
      const output = this.recentOutput.join("\n");
      throw new Error(
        `${error.message}${output ? `\nUltima salida del backend:\n${output}` : ""}`,
      );
    }

    this.isReady = true;
    this.logger.info("FastAPI ha respondido correctamente a /api/health.");
    return { baseUrl: this.baseUrl, port: this.port };
  }

  captureOutput(stream, channel) {
    stream?.setEncoding("utf8");
    stream?.on("data", (chunk) => {
      for (const line of chunk.split(/\r?\n/).filter(Boolean)) {
        const formattedLine = `[backend ${channel}] ${line}`;
        this.recentOutput.push(formattedLine);
        this.recentOutput = this.recentOutput.slice(-30);
        if (channel === "stderr") {
          this.logger.warn(formattedLine);
        } else {
          this.logger.info(formattedLine);
        }
      }
    });
  }

  async stop() {
    if (!this.childProcess) {
      return;
    }
    this.isStopping = true;
    this.logger.info("Solicitando el cierre cooperativo de FastAPI.");
    try {
      await stopChildProcess(this.childProcess);
    } finally {
      this.childProcess = null;
      this.logger.info("El proceso backend ha terminado.");
    }
  }
}

module.exports = {
  BackendProcess,
  findFreePort,
  stopChildProcess,
  waitForHttpEndpoint,
};
