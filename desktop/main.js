"use strict";

const path = require("node:path");

const { acquireSingleInstance } = require("./applicationLifecycle");
const {
  BackendProcess,
  waitForHttpEndpoint,
} = require("./backendProcess");
const { DesktopLogger } = require("./logger");
const {
  ensureRuntimeDirectories,
  resolveRuntimePaths,
  validateRuntimeResources,
} = require("./runtimePaths");
const { createWindowOptions } = require("./windowConfiguration");
const { readWindowState, writeWindowState } = require("./windowState");

const DEVELOPMENT_URL = "http://127.0.0.1:5173";

function isSafeExternalUrl(targetUrl) {
  try {
    const parsedUrl = new URL(targetUrl);
    return parsedUrl.protocol === "https:" || parsedUrl.protocol === "http:";
  } catch {
    return false;
  }
}

function configureNavigation(window, allowedOrigin, shell) {
  window.webContents.on("will-navigate", (event, targetUrl) => {
    const targetOrigin = new URL(targetUrl).origin;
    if (targetOrigin === allowedOrigin) {
      return;
    }
    event.preventDefault();
    if (isSafeExternalUrl(targetUrl)) {
      void shell.openExternal(targetUrl);
    }
  });
  window.webContents.setWindowOpenHandler(({ url }) => {
    if (isSafeExternalUrl(url)) {
      void shell.openExternal(url);
    }
    return { action: "deny" };
  });
  window.webContents.on("will-attach-webview", (event) => {
    event.preventDefault();
  });
  window.webContents.session.setPermissionRequestHandler(
    (_webContents, _permission, callback) => callback(false),
  );
}

function createDesktopRuntime(electron) {
  const {
    app,
    BrowserWindow,
    dialog,
    Menu,
    screen,
    shell,
  } = electron;
  let mainWindow = null;
  let backendProcess = null;
  let logger = null;
  let isShuttingDown = false;
  let stateSaveTimer = null;

  async function shutdown(exitCode = 0) {
    if (isShuttingDown) {
      return;
    }
    isShuttingDown = true;
    logger?.info("Iniciando cierre completo de SoundShelf.");
    if (stateSaveTimer) {
      clearTimeout(stateSaveTimer);
    }
    try {
      await backendProcess?.stop();
    } catch (error) {
      logger?.error("No se pudo cerrar el backend de forma limpia.", error);
    }
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.destroy();
    }
    logger?.info(`SoundShelf finaliza con codigo ${exitCode}.`);
    app.exit(exitCode);
  }

  async function start() {
    const paths = resolveRuntimePaths({
      isPackaged: app.isPackaged,
      appPath: app.isPackaged
        ? app.getAppPath()
        : path.resolve(__dirname, ".."),
      resourcesPath: process.resourcesPath,
      userDataPath: app.getPath("userData"),
    });
    ensureRuntimeDirectories(paths);
    logger = new DesktopLogger(paths.electronLogPath);
    logger.info(
      `Iniciando SoundShelf ${app.isPackaged ? "empaquetado" : "en desarrollo"}.`,
    );
    validateRuntimeResources(paths);

    app.setAppUserModelId("com.soundshelf.desktop");
    Menu.setApplicationMenu(null);
    backendProcess = new BackendProcess({
      paths,
      logger,
      onUnexpectedExit: (error) => {
        if (isShuttingDown) {
          return;
        }
        logger.error("FastAPI se ha cerrado mientras la aplicacion seguia activa.", error);
        dialog.showErrorBox(
          "SoundShelf se ha detenido",
          "El servicio local de SoundShelf se cerró inesperadamente. " +
            `Consulta ${paths.electronLogPath} para ver los detalles.`,
        );
        void shutdown(1);
      },
    });
    const { baseUrl } = await backendProcess.start();

    const frontendBaseUrl = app.isPackaged ? baseUrl : DEVELOPMENT_URL;
    if (!app.isPackaged) {
      logger.info(`Esperando a Vite en ${DEVELOPMENT_URL}.`);
      await waitForHttpEndpoint(DEVELOPMENT_URL, { timeoutMs: 45_000 });
    }

    const savedBounds = readWindowState(
      paths.windowStatePath,
      screen.getAllDisplays(),
    );
    mainWindow = new BrowserWindow(
      createWindowOptions({
        bounds: savedBounds,
        enableDevTools: !app.isPackaged,
        iconPath: paths.iconPath,
        preloadPath: path.join(__dirname, "preload.js"),
      }),
    );
    if (!savedBounds) {
      mainWindow.center();
    }

    const frontendUrl = new URL(frontendBaseUrl);
    frontendUrl.searchParams.set("apiBaseUrl", baseUrl);
    configureNavigation(mainWindow, frontendUrl.origin, shell);

    const saveBounds = () => {
      if (stateSaveTimer) {
        clearTimeout(stateSaveTimer);
      }
      stateSaveTimer = setTimeout(() => {
        if (
          mainWindow &&
          !mainWindow.isDestroyed() &&
          !mainWindow.isMaximized() &&
          !mainWindow.isMinimized()
        ) {
          writeWindowState(paths.windowStatePath, mainWindow.getBounds());
        }
      }, 250);
    };
    mainWindow.on("resize", saveBounds);
    mainWindow.on("move", saveBounds);
    mainWindow.on("close", (event) => {
      if (!isShuttingDown) {
        event.preventDefault();
        void shutdown(0);
      }
    });
    mainWindow.once("ready-to-show", () => {
      mainWindow.show();
      logger.info("La ventana principal de SoundShelf esta visible.");
    });
    if (!app.isPackaged) {
      mainWindow.webContents.on("before-input-event", (event, input) => {
        const opensDevTools =
          input.key === "F12" ||
          (input.control && input.shift && input.key.toLowerCase() === "i");
        if (opensDevTools) {
          event.preventDefault();
          mainWindow.webContents.toggleDevTools();
        }
      });
    }
    await mainWindow.loadURL(frontendUrl.toString());
    logger.info(`Frontend cargado desde ${frontendBaseUrl}.`);

    const smokeTestMilliseconds = Number(
      process.env.SOUNDSHELF_SMOKE_TEST_MS || 0,
    );
    if (
      !app.isPackaged &&
      Number.isFinite(smokeTestMilliseconds) &&
      smokeTestMilliseconds > 0
    ) {
      setTimeout(() => {
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.close();
        }
      }, smokeTestMilliseconds);
    }
  }

  function handleFatalError(error) {
    const normalizedError =
      error instanceof Error ? error : new Error(String(error));
    logger?.error("SoundShelf no ha podido iniciar.", normalizedError);
    dialog.showErrorBox(
      "No se pudo iniciar SoundShelf",
      `${normalizedError.message}\n\nConsulta el log de Electron para más detalles.`,
    );
    void shutdown(1);
  }

  return {
    getWindow: () => mainWindow,
    handleFatalError,
    shutdown,
    start,
  };
}

function bootstrap() {
  const electron = require("electron");
  const { app } = electron;
  app.setName("SoundShelf");
  if (process.env.SOUNDSHELF_DATA_DIR) {
    app.setPath(
      "userData",
      path.resolve(process.env.SOUNDSHELF_DATA_DIR),
    );
  }
  let runtime = null;
  if (!acquireSingleInstance(app, () => runtime?.getWindow())) {
    return;
  }

  app.on("window-all-closed", () => {
    app.quit();
  });
  app.on("before-quit", (event) => {
    if (!runtime) {
      return;
    }
    event.preventDefault();
    void runtime.shutdown(0);
  });
  process.on("uncaughtException", (error) => {
    runtime?.handleFatalError(error);
  });
  process.on("unhandledRejection", (error) => {
    runtime?.handleFatalError(error);
  });

  app.whenReady().then(() => {
    runtime = createDesktopRuntime(electron);
    return runtime.start();
  }).catch((error) => {
    if (runtime) {
      runtime.handleFatalError(error);
      return;
    }
    electron.dialog.showErrorBox(
      "No se pudo iniciar SoundShelf",
      error instanceof Error ? error.message : String(error),
    );
    app.exit(1);
  });
}

if (process.versions.electron) {
  bootstrap();
}

module.exports = {
  configureNavigation,
  createDesktopRuntime,
  isSafeExternalUrl,
};
