"use strict";

const assert = require("node:assert/strict");
const { spawn } = require("node:child_process");
const http = require("node:http");
const net = require("node:net");
const test = require("node:test");

const {
  findFreePort,
  stopChildProcess,
  waitForHttpEndpoint,
} = require("../backendProcess");

test("findFreePort returns a loopback port that can be bound", async () => {
  const port = await findFreePort();
  const server = net.createServer();

  await new Promise((resolve, reject) => {
    server.once("error", reject);
    server.listen(port, "127.0.0.1", resolve);
  });
  await new Promise((resolve) => server.close(resolve));

  assert.ok(port > 0 && port <= 65_535);
});

test("waitForHttpEndpoint waits until the health endpoint responds", async () => {
  const port = await findFreePort();
  const server = http.createServer((_request, response) => {
    response.writeHead(200, { "Content-Type": "application/json" });
    response.end('{"status":"ok"}');
  });
  await new Promise((resolve) => server.listen(port, "127.0.0.1", resolve));

  await waitForHttpEndpoint(`http://127.0.0.1:${port}/api/health`, {
    timeoutMs: 1_000,
  });

  await new Promise((resolve) => server.close(resolve));
});

test("waitForHttpEndpoint reports startup errors without waiting for timeout", async () => {
  const startupError = new Error("backend failed");

  await assert.rejects(
    waitForHttpEndpoint("http://127.0.0.1:1/api/health", {
      timeoutMs: 5_000,
      getStartupError: () => startupError,
    }),
    /backend failed/,
  );
});

test("stopChildProcess uses the cooperative stdin shutdown channel", async () => {
  const child = spawn(
    process.execPath,
    [
      "-e",
      [
        "process.stdin.setEncoding('utf8');",
        "process.stdin.on('data', value => {",
        "if (value.includes('shutdown')) process.exit(0);",
        "});",
        "setInterval(() => {}, 1000);",
      ].join(""),
    ],
    { stdio: ["pipe", "ignore", "ignore"] },
  );

  await stopChildProcess(child, { gracefulTimeoutMs: 2_000 });

  assert.equal(child.exitCode, 0);
});
