"use strict";

const fs = require("node:fs");
const path = require("node:path");

function resolveRuntimePaths({
  isPackaged,
  appPath,
  resourcesPath,
  userDataPath,
  identity,
  platform = process.platform,
  environment = process.env,
}) {
  const executableExtension = platform === "win32" ? ".exe" : "";
  const projectDirectory = isPackaged ? resourcesPath : appPath;
  const dataDirectory = path.resolve(userDataPath);
  const logsDirectory = path.join(dataDirectory, "logs");
  const temporaryDirectory = path.join(dataDirectory, "temp");
  const frontendDirectory = isPackaged
    ? path.join(resourcesPath, "frontend")
    : path.join(appPath, "frontend", "dist");
  const backendDirectory = isPackaged
    ? path.join(resourcesPath, "backend")
    : null;
  const backendExecutable = backendDirectory
    ? path.join(
        backendDirectory,
        `SoundShelfBackend${executableExtension}`,
      )
    : null;
  const ffmpegPath = isPackaged
    ? path.join(resourcesPath, "ffmpeg", `ffmpeg${executableExtension}`)
    : environment.FFMPEG_PATH ||
      path.join(
        appPath,
        "node_modules",
        "ffmpeg-static",
        `ffmpeg${executableExtension}`,
      );

  return {
    isPackaged,
    channel: identity.channel,
    productName: identity.productName,
    appId: identity.appId,
    projectDirectory,
    dataDirectory,
    logsDirectory,
    temporaryDirectory,
    frontendDirectory,
    backendDirectory,
    backendExecutable,
    pythonExecutable:
      environment.PYTHON_EXECUTABLE ||
      (platform === "win32" ? "python" : "python3"),
    databasePath: path.join(dataDirectory, "soundshelf.db"),
    backendLogPath: path.join(logsDirectory, "backend.log"),
    electronLogPath: path.join(logsDirectory, "electron.log"),
    windowStatePath: path.join(dataDirectory, "windowState.json"),
    ffmpegPath,
    iconPath: isPackaged
      ? path.join(resourcesPath, "icon", "applicationIcon.png")
      : path.join(
          appPath,
          "desktop",
          "assets",
          identity.iconFileName,
        ),
  };
}

function ensureRuntimeDirectories(paths) {
  for (const directory of [
    paths.dataDirectory,
    paths.logsDirectory,
    paths.temporaryDirectory,
  ]) {
    fs.mkdirSync(directory, { recursive: true });
  }
}

function validateRuntimeResources(paths) {
  const requiredFiles = [
    [paths.iconPath, `el icono de ${paths.productName}`],
    [paths.ffmpegPath, "el ejecutable FFmpeg incluido"],
  ];
  if (paths.isPackaged) {
    requiredFiles.push(
      [paths.backendExecutable, "el backend empaquetado"],
      [path.join(paths.frontendDirectory, "index.html"), "el build de React"],
    );
  }

  const missingResources = requiredFiles
    .filter(([filePath]) => !filePath || !fs.existsSync(filePath))
    .map(([filePath, description]) => `${description}: ${filePath}`);
  if (missingResources.length > 0) {
    throw new Error(
      `Faltan recursos necesarios para iniciar ${paths.productName}:\n${missingResources.join("\n")}`,
    );
  }
}

function databaseUrlFromPath(databasePath) {
  return `sqlite:///${path.resolve(databasePath).replaceAll("\\", "/")}`;
}

function buildBackendEnvironment(
  paths,
  port,
  inheritedEnvironment = process.env,
) {
  const environment = {
    ...inheritedEnvironment,
    APP_NAME: paths.productName,
    APP_ENV: paths.isPackaged ? "production" : "development",
    API_HOST: "127.0.0.1",
    API_PORT: String(port),
    SOUNDSHELF_PORT: String(port),
    SOUNDSHELF_CHANNEL: paths.channel,
    SOUNDSHELF_DATA_DIR: paths.dataDirectory,
    DATABASE_URL: databaseUrlFromPath(paths.databasePath),
    LOG_FILE: paths.backendLogPath,
    TEMPORARY_FOLDER: paths.temporaryDirectory,
    FFMPEG_PATH: paths.ffmpegPath,
    PYTHONIOENCODING: "utf-8",
    PYTHONUNBUFFERED: "1",
  };

  if (paths.isPackaged) {
    environment.SOUNDSHELF_FRONTEND_DIR = paths.frontendDirectory;
  } else {
    delete environment.SOUNDSHELF_FRONTEND_DIR;
    delete environment.FRONTEND_DIRECTORY;
  }
  return environment;
}

function createBackendSpawnConfiguration(paths, port) {
  if (paths.isPackaged) {
    return {
      command: paths.backendExecutable,
      arguments: [],
      options: {
        cwd: paths.backendDirectory,
        env: buildBackendEnvironment(paths, port),
      },
    };
  }

  return {
    command: paths.pythonExecutable,
    arguments: ["-m", "app.desktopMain"],
    options: {
      cwd: paths.projectDirectory,
      env: buildBackendEnvironment(paths, port),
    },
  };
}

module.exports = {
  buildBackendEnvironment,
  createBackendSpawnConfiguration,
  databaseUrlFromPath,
  ensureRuntimeDirectories,
  resolveRuntimePaths,
  validateRuntimeResources,
};
