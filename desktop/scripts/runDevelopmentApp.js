"use strict";

const { execFile, spawn } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const PROJECT_ROOT = path.resolve(__dirname, "..", "..");
const FRONTEND_ROOT = path.join(PROJECT_ROOT, "frontend");
const ELECTRON_MAIN = path.join(PROJECT_ROOT, "desktop", "main.js");

function resolvePackageBinary(packageName, binaryName, lookupPaths) {
  const packageJsonPath = require.resolve(`${packageName}/package.json`, {
    paths: lookupPaths,
  });
  const packageRoot = path.dirname(packageJsonPath);
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, "utf8"));
  const binaryPath =
    typeof packageJson.bin === "string"
      ? packageJson.bin
      : packageJson.bin?.[binaryName];

  if (!binaryPath) {
    throw new Error(`No se encontro el binario ${binaryName} de ${packageName}.`);
  }

  return path.join(packageRoot, binaryPath);
}

function resolveElectronExecutable() {
  const electronExecutable = require("electron");
  if (typeof electronExecutable !== "string") {
    throw new Error("No se pudo resolver el ejecutable de Electron.");
  }
  return electronExecutable;
}

function removeElectronNodeMode(environment) {
  return Object.fromEntries(
    Object.entries(environment).filter(
      ([name]) => name.toUpperCase() !== "ELECTRON_RUN_AS_NODE",
    ),
  );
}

function createLaunchConfiguration({
  projectRoot = PROJECT_ROOT,
  frontendRoot = FRONTEND_ROOT,
  electronMain = ELECTRON_MAIN,
  nodeExecutable = process.execPath,
  electronExecutable = resolveElectronExecutable(),
  viteBinary = resolvePackageBinary("vite", "vite", [frontendRoot]),
  environment = process.env,
} = {}) {
  return {
    vite: {
      name: "vite",
      command: nodeExecutable,
      arguments: [viteBinary, "--host", "127.0.0.1"],
      options: {
        cwd: frontendRoot,
        env: {
          ...environment,
          BROWSER: "none",
        },
      },
    },
    electron: {
      name: "electron",
      command: electronExecutable,
      arguments: [electronMain],
      options: {
        cwd: projectRoot,
        env: removeElectronNodeMode(environment),
      },
    },
  };
}

function spawnManagedProcess(configuration, spawnImpl = spawn) {
  return spawnImpl(configuration.command, configuration.arguments, {
    ...configuration.options,
    shell: false,
    stdio: "inherit",
    windowsHide: true,
  });
}

function getExitCode(code, signal) {
  if (typeof code === "number") {
    return code;
  }
  if (signal === "SIGINT") {
    return 130;
  }
  if (signal) {
    return 1;
  }
  return 0;
}

function waitForChildExit(childProcess, timeoutMs = 0) {
  if (!childProcess || childProcess.exitCode !== null || childProcess.signalCode) {
    return Promise.resolve({
      code: childProcess?.exitCode ?? null,
      signal: childProcess?.signalCode ?? null,
      timedOut: false,
    });
  }

  return new Promise((resolve) => {
    let timeout = null;
    const onExit = (code, signal) => {
      if (timeout) {
        clearTimeout(timeout);
      }
      resolve({ code, signal, timedOut: false });
    };

    childProcess.once("exit", onExit);
    if (timeoutMs > 0) {
      timeout = setTimeout(() => {
        childProcess.removeListener("exit", onExit);
        resolve({ code: null, signal: null, timedOut: true });
      }, timeoutMs);
    }
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
          return;
        }
        resolve();
      },
    );
  });
}

async function stopProcessTree(
  childProcess,
  {
    platform = process.platform,
    gracefulTimeoutMs = 2_000,
    forceTimeoutMs = 5_000,
    execFileImpl = execFile,
  } = {},
) {
  if (!childProcess || childProcess.exitCode !== null || childProcess.signalCode) {
    return;
  }

  if (platform === "win32") {
    await killWindowsProcessTree(childProcess.pid, execFileImpl);
    await waitForChildExit(childProcess, forceTimeoutMs);
    return;
  }

  childProcess.kill("SIGTERM");
  const gracefulExit = await waitForChildExit(childProcess, gracefulTimeoutMs);
  if (!gracefulExit.timedOut) {
    return;
  }

  childProcess.kill("SIGKILL");
  await waitForChildExit(childProcess, forceTimeoutMs);
}

function createExitWatcher({ viteProcess, electronProcess, signalEmitter = process }) {
  return new Promise((resolve) => {
    let resolved = false;
    const signalHandlers = new Map();
    const cleanup = () => {
      electronProcess.removeListener("exit", onElectronExit);
      electronProcess.removeListener("error", onElectronError);
      viteProcess.removeListener("exit", onViteExit);
      viteProcess.removeListener("error", onViteError);
      for (const [signal, handler] of signalHandlers) {
        signalEmitter.removeListener(signal, handler);
      }
    };
    const finish = (result) => {
      if (resolved) {
        return;
      }
      resolved = true;
      cleanup();
      resolve(result);
    };

    const onElectronExit = (code, signal) => {
      finish({
        reason: "electron-exit",
        exitCode: getExitCode(code, signal),
        stopElectron: false,
        stopVite: true,
      });
    };
    const onElectronError = (error) => {
      finish({
        reason: "electron-error",
        error,
        exitCode: 1,
        stopElectron: false,
        stopVite: true,
      });
    };

    const onViteExit = (code, signal) => {
      finish({
        reason: "vite-exit",
        exitCode: getExitCode(code, signal) || 1,
        stopElectron: true,
        stopVite: false,
      });
    };
    const onViteError = (error) => {
      finish({
        reason: "vite-error",
        error,
        exitCode: 1,
        stopElectron: true,
        stopVite: false,
      });
    };

    electronProcess.once("exit", onElectronExit);
    electronProcess.once("error", onElectronError);
    viteProcess.once("exit", onViteExit);
    viteProcess.once("error", onViteError);

    for (const signal of ["SIGINT", "SIGTERM", "SIGHUP"]) {
      const signalHandler = () => {
        finish({
          reason: "parent-signal",
          exitCode: signal === "SIGINT" ? 130 : 1,
          stopElectron: true,
          stopVite: true,
        });
      };
      signalHandlers.set(signal, signalHandler);
      signalEmitter.once(signal, signalHandler);
    }
  });
}

async function runDevelopmentApp({
  createConfiguration = createLaunchConfiguration,
  spawnImpl = spawn,
  stopTree = stopProcessTree,
  log = console.log,
  errorLog = console.error,
} = {}) {
  const configuration = createConfiguration();
  log("[app] Iniciando Vite en desarrollo.");
  const viteProcess = spawnManagedProcess(configuration.vite, spawnImpl);
  log("[app] Iniciando Electron.");
  const electronProcess = spawnManagedProcess(configuration.electron, spawnImpl);

  const result = await createExitWatcher({ viteProcess, electronProcess });
  if (result.error) {
    errorLog(`[app] ${result.error.message}`);
  }
  if (result.reason === "electron-exit" && result.exitCode === 0) {
    log("[app] Electron se cerro correctamente. Cerrando Vite.");
  }

  await Promise.all([
    result.stopElectron ? stopTree(electronProcess) : waitForChildExit(electronProcess),
    result.stopVite ? stopTree(viteProcess) : waitForChildExit(viteProcess),
  ]);

  return result.exitCode;
}

if (require.main === module) {
  runDevelopmentApp()
    .then((exitCode) => {
      process.exitCode = exitCode;
    })
    .catch((error) => {
      console.error(`[app] ${error instanceof Error ? error.message : String(error)}`);
      process.exitCode = 1;
    });
}

module.exports = {
  createExitWatcher,
  createLaunchConfiguration,
  getExitCode,
  killWindowsProcessTree,
  removeElectronNodeMode,
  resolvePackageBinary,
  runDevelopmentApp,
  stopProcessTree,
  waitForChildExit,
};
