"use strict";

const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const { BackendProcess } = require("../backendProcess");
const { DesktopLogger } = require("../logger");
const {
  ensureRuntimeDirectories,
  resolveRuntimePaths,
} = require("../runtimePaths");

async function main() {
  const projectDirectory = path.resolve(__dirname, "..", "..");
  const dataDirectory = fs.mkdtempSync(
    path.join(os.tmpdir(), "soundshelf-backend-bundle-"),
  );
  const paths = resolveRuntimePaths({
    isPackaged: true,
    appPath: projectDirectory,
    resourcesPath: projectDirectory,
    userDataPath: dataDirectory,
    platform: "win32",
    environment: {},
  });
  paths.backendDirectory = path.join(
    projectDirectory,
    ".desktopBuild",
    "backend",
    "SoundShelfBackend",
  );
  paths.backendExecutable = path.join(
    paths.backendDirectory,
    "SoundShelfBackend.exe",
  );
  paths.frontendDirectory = path.join(projectDirectory, "frontend", "dist");
  paths.ffmpegPath = path.join(
    projectDirectory,
    "node_modules",
    "ffmpeg-static",
    "ffmpeg.exe",
  );
  ensureRuntimeDirectories(paths);

  const logger = new DesktopLogger(
    path.join(paths.logsDirectory, "bundleVerification.log"),
  );
  const backend = new BackendProcess({ paths, logger });
  try {
    const { baseUrl } = await backend.start();
    const [healthResponse, frontendResponse, capabilitiesResponse] =
      await Promise.all([
        fetch(`${baseUrl}/api/health`),
        fetch(`${baseUrl}/`),
        fetch(`${baseUrl}/api/capabilities`),
      ]);
    const health = await healthResponse.json();
    const frontend = await frontendResponse.text();
    const capabilities = await capabilitiesResponse.json();

    if (
      health.status !== "ok" ||
      !frontend.includes('<div id="root"></div>') ||
      capabilities.ffmpegAvailable !== true ||
      !fs.existsSync(paths.databasePath)
    ) {
      throw new Error(
        "El backend empaquetado no supero la verificacion funcional.",
      );
    }
    console.log(
      `Backend empaquetado verificado en ${baseUrl}; datos temporales: ${dataDirectory}`,
    );
  } finally {
    await backend.stop();
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
