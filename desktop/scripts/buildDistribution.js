"use strict";

const { execFileSync, spawnSync } = require("node:child_process");
const path = require("node:path");

const {
  BETA_CHANNEL,
  PRODUCTION_CHANNEL,
  getApplicationIdentity,
} = require("../applicationIdentity");

function getCurrentGitBranch() {
  try {
    return execFileSync("git", ["branch", "--show-current"], {
      cwd: path.resolve(__dirname, "..", ".."),
      encoding: "utf8",
      windowsHide: true,
    }).trim();
  } catch (error) {
    throw new Error(
      `❌ Unable to determine the current Git branch.\n${error.message}`,
    );
  }
}

function assertBranchAllowed(channel, branch) {
  getApplicationIdentity(channel);

  if (!branch) {
    throw new Error(
      "❌ Unable to determine the current Git branch. " +
        "Distribution builds require a named branch.",
    );
  }
  if (channel === PRODUCTION_CHANNEL && branch !== "main") {
    throw new Error(
      [
        "❌ Production builds are only allowed from the main branch.",
        "Current branch:",
        branch,
      ].join("\n"),
    );
  }
  if (channel === BETA_CHANNEL && branch === "main") {
    throw new Error("❌ Beta builds cannot be generated from main.");
  }
}

function runProcess(command, arguments_, options = {}) {
  const result = spawnSync(command, arguments_, {
    cwd: path.resolve(__dirname, "..", ".."),
    env: options.environment || process.env,
    stdio: "inherit",
    windowsHide: true,
  });
  if (result.error) {
    throw result.error;
  }
  if (result.status !== 0) {
    const error = new Error(
      `${options.description || command} failed with exit code ${result.status}.`,
    );
    error.exitCode = result.status || 1;
    throw error;
  }
}

function runNpmScript(scriptName) {
  const npmExecutable = process.env.npm_execpath;
  if (npmExecutable) {
    runProcess(process.execPath, [npmExecutable, "run", scriptName], {
      description: `npm run ${scriptName}`,
    });
    return;
  }

  runProcess(
    process.platform === "win32" ? "npm.cmd" : "npm",
    ["run", scriptName],
    { description: `npm run ${scriptName}` },
  );
}

function buildDistribution(channel, { directoryOnly = false } = {}) {
  const currentBranch = getCurrentGitBranch();
  assertBranchAllowed(channel, currentBranch);

  runNpmScript("build:frontend");
  runNpmScript("build:backend");

  const builderCli = require.resolve("electron-builder/out/cli/cli.js");
  const configurationPath = path.resolve(
    __dirname,
    "..",
    "electronBuilderConfig.js",
  );
  runProcess(
    process.execPath,
    [
      builderCli,
      "--config",
      configurationPath,
      "--win",
      directoryOnly ? "--dir" : "nsis",
    ],
    {
      description: "electron-builder",
      environment: {
        ...process.env,
        SOUNDSHELF_DISTRIBUTION_CHANNEL: channel,
      },
    },
  );
}

function main() {
  const channel = process.argv[2];
  const directoryOnly = process.argv.includes("--dir");

  try {
    buildDistribution(channel, { directoryOnly });
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = error.exitCode || 1;
  }
}

if (require.main === module) {
  main();
}

module.exports = {
  assertBranchAllowed,
  buildDistribution,
  getCurrentGitBranch,
};
