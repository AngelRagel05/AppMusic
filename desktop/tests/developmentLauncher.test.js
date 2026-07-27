"use strict";

const assert = require("node:assert/strict");
const { EventEmitter } = require("node:events");
const path = require("node:path");
const test = require("node:test");

const {
  createExitWatcher,
  createLaunchConfiguration,
  getExitCode,
  removeElectronNodeMode,
  runDevelopmentApp,
} = require("../scripts/runDevelopmentApp");

test("development launcher starts Vite and Electron directly", () => {
  const projectRoot = path.resolve("C:\\workspace\\SoundShelf");
  const frontendRoot = path.join(projectRoot, "frontend");
  const electronMain = path.join(projectRoot, "desktop", "main.js");
  const nodeExecutable = "node.exe";
  const electronExecutable = "electron.exe";
  const viteBinary = path.join(frontendRoot, "node_modules", "vite", "bin", "vite.js");

  const configuration = createLaunchConfiguration({
    projectRoot,
    frontendRoot,
    electronMain,
    nodeExecutable,
    electronExecutable,
    viteBinary,
    environment: { ELECTRON_RUN_AS_NODE: "1", SOUNDSHELF_TEST: "1" },
  });

  assert.equal(configuration.vite.command, nodeExecutable);
  assert.equal(configuration.vite.options.cwd, frontendRoot);
  assert.deepEqual(
    configuration.vite.arguments.slice(-2),
    ["--host", "127.0.0.1"],
  );
  assert.equal(configuration.electron.command, electronExecutable);
  assert.deepEqual(configuration.electron.arguments, [electronMain]);
  assert.equal(configuration.electron.options.env.ELECTRON_RUN_AS_NODE, undefined);
  assert.equal(configuration.electron.options.env.SOUNDSHELF_TEST, "1");
});

test("development launcher removes Electron node mode case-insensitively", () => {
  assert.deepEqual(
    removeElectronNodeMode({
      Electron_Run_As_Node: "1",
      PATH: "C:\\bin",
    }),
    { PATH: "C:\\bin" },
  );
});

test("development launcher maps a normal Electron close to exit code 0", async () => {
  const viteProcess = new EventEmitter();
  const electronProcess = new EventEmitter();
  viteProcess.exitCode = null;
  viteProcess.signalCode = null;
  electronProcess.exitCode = null;
  electronProcess.signalCode = null;

  const watcher = createExitWatcher({ viteProcess, electronProcess });
  electronProcess.emit("exit", 0, null);

  assert.deepEqual(await watcher, {
    reason: "electron-exit",
    exitCode: 0,
    stopElectron: false,
    stopVite: true,
  });
});

test("runDevelopmentApp stops Vite after a normal Electron close", async () => {
  const processes = new Map();
  const stopped = [];

  function createFakeProcess(name) {
    const childProcess = new EventEmitter();
    childProcess.pid = name === "vite" ? 10 : 11;
    childProcess.exitCode = null;
    childProcess.signalCode = null;
    processes.set(name, childProcess);
    return childProcess;
  }

  const exitCodePromise = runDevelopmentApp({
    createConfiguration: () => ({
      vite: {
        name: "vite",
        command: "node",
        arguments: ["vite"],
        options: {},
      },
      electron: {
        name: "electron",
        command: "electron",
        arguments: ["desktop/main.js"],
        options: {},
      },
    }),
    spawnImpl: (command) =>
      createFakeProcess(command === "node" ? "vite" : "electron"),
    stopTree: async (childProcess) => {
      stopped.push(childProcess.pid);
      childProcess.exitCode = 1;
      childProcess.emit("exit", 1, null);
    },
    log: () => {},
    errorLog: () => {},
  });

  const electronProcess = processes.get("electron");
  electronProcess.exitCode = 0;
  electronProcess.emit("exit", 0, null);

  assert.equal(await exitCodePromise, 0);
  assert.deepEqual(stopped, [10]);
});

test("getExitCode keeps non-zero child failures visible", () => {
  assert.equal(getExitCode(0, null), 0);
  assert.equal(getExitCode(7, null), 7);
  assert.equal(getExitCode(null, "SIGINT"), 130);
  assert.equal(getExitCode(null, "SIGTERM"), 1);
});
