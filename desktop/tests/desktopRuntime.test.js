"use strict";

const assert = require("node:assert/strict");
const { EventEmitter } = require("node:events");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");

const { acquireSingleInstance } = require("../applicationLifecycle");
const {
  buildBackendEnvironment,
  createBackendSpawnConfiguration,
  resolveRuntimePaths,
} = require("../runtimePaths");
const { createWindowOptions } = require("../windowConfiguration");
const { readWindowState, writeWindowState } = require("../windowState");

test("production paths keep persistent data outside application resources", () => {
  const paths = resolveRuntimePaths({
    isPackaged: true,
    appPath: "C:\\Program Files\\SoundShelf\\resources\\app.asar",
    resourcesPath: "C:\\Program Files\\SoundShelf\\resources",
    userDataPath: "C:\\Users\\Test\\AppData\\Roaming\\SoundShelf",
    platform: "win32",
    environment: {},
  });
  const environment = buildBackendEnvironment(paths, 43_125, {});
  const launch = createBackendSpawnConfiguration(paths, 43_125);

  assert.equal(
    paths.databasePath,
    path.resolve(
      "C:\\Users\\Test\\AppData\\Roaming\\SoundShelf",
      "soundshelf.db",
    ),
  );
  assert.match(paths.backendExecutable, /SoundShelfBackend\.exe$/);
  assert.equal(environment.SOUNDSHELF_PORT, "43125");
  assert.equal(environment.SOUNDSHELF_DATA_DIR, paths.dataDirectory);
  assert.equal(environment.SOUNDSHELF_FRONTEND_DIR, paths.frontendDirectory);
  assert.match(environment.DATABASE_URL, /^sqlite:\/\/\//);
  assert.equal(launch.command, paths.backendExecutable);
});

test("development launches the Python module without configuring static React", () => {
  const paths = resolveRuntimePaths({
    isPackaged: false,
    appPath: "C:\\workspace\\SoundShelf",
    resourcesPath: "C:\\workspace\\SoundShelf\\node_modules\\electron",
    userDataPath: "C:\\Users\\Test\\AppData\\Roaming\\SoundShelf",
    platform: "win32",
    environment: { PYTHON_EXECUTABLE: "py" },
  });
  const launch = createBackendSpawnConfiguration(paths, 43_126);

  assert.equal(launch.command, "py");
  assert.deepEqual(launch.arguments, ["-m", "app.desktopMain"]);
  assert.equal(launch.options.env.SOUNDSHELF_FRONTEND_DIR, undefined);
});

test("single instance lock quits duplicates and focuses the original window", () => {
  class FakeApp extends EventEmitter {
    constructor(hasLock) {
      super();
      this.hasLock = hasLock;
      this.quitCount = 0;
    }

    requestSingleInstanceLock() {
      return this.hasLock;
    }

    quit() {
      this.quitCount += 1;
    }
  }

  const duplicateApp = new FakeApp(false);
  assert.equal(acquireSingleInstance(duplicateApp, () => null), false);
  assert.equal(duplicateApp.quitCount, 1);

  const app = new FakeApp(true);
  const calls = [];
  const window = {
    isDestroyed: () => false,
    isMinimized: () => true,
    restore: () => calls.push("restore"),
    show: () => calls.push("show"),
    focus: () => calls.push("focus"),
  };
  assert.equal(acquireSingleInstance(app, () => window), true);
  app.emit("second-instance");
  assert.deepEqual(calls, ["restore", "show", "focus"]);
});

test("window security options keep Node and privileged APIs isolated", () => {
  const options = createWindowOptions({
    bounds: null,
    enableDevTools: false,
    iconPath: "icon.png",
    preloadPath: "preload.js",
  });

  assert.equal(options.frame, true);
  assert.equal(options.webPreferences.contextIsolation, true);
  assert.equal(options.webPreferences.nodeIntegration, false);
  assert.equal(options.webPreferences.sandbox, true);
  assert.equal(options.webPreferences.webSecurity, true);
  assert.equal(options.webPreferences.devTools, false);
  assert.equal(options.webPreferences.webviewTag, false);
});

test("window bounds persist only when they intersect an active display", () => {
  const temporaryDirectory = fs.mkdtempSync(
    path.join(os.tmpdir(), "soundshelf-window-"),
  );
  const statePath = path.join(temporaryDirectory, "windowState.json");
  const bounds = { x: 20, y: 30, width: 1280, height: 800 };
  const displays = [
    { workArea: { x: 0, y: 0, width: 1920, height: 1080 } },
  ];

  writeWindowState(statePath, bounds);

  assert.deepEqual(readWindowState(statePath, displays), bounds);
  assert.equal(
    readWindowState(statePath, [
      { workArea: { x: 3000, y: 0, width: 1920, height: 1080 } },
    ]),
    null,
  );
});
