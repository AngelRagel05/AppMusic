"use strict";

const assert = require("node:assert/strict");
const path = require("node:path");
const test = require("node:test");

const {
  BETA_CHANNEL,
  PRODUCTION_CHANNEL,
  getApplicationIdentity,
  resolveApplicationIdentity,
  resolveDefaultUserDataPath,
} = require("../applicationIdentity");
const {
  createBuilderConfiguration,
} = require("../distributionConfiguration");
const {
  assertBranchAllowed,
} = require("../scripts/buildDistribution");
const { resolveRuntimePaths } = require("../runtimePaths");

test("production and beta expose independent Windows identities", () => {
  const production = getApplicationIdentity(PRODUCTION_CHANNEL);
  const beta = getApplicationIdentity(BETA_CHANNEL);

  assert.deepEqual(
    {
      productName: production.productName,
      appId: production.appId,
      executableName: production.executableName,
      installerArtifactName: production.installerArtifactName,
    },
    {
      productName: "SoundShelf",
      appId: "com.angelragel.soundshelf",
      executableName: "SoundShelf",
      installerArtifactName: "SoundShelf Setup.${ext}",
    },
  );
  assert.deepEqual(
    {
      productName: beta.productName,
      appId: beta.appId,
      executableName: beta.executableName,
      installerArtifactName: beta.installerArtifactName,
    },
    {
      productName: "SoundShelf Beta",
      appId: "com.angelragel.soundshelf.beta",
      executableName: "SoundShelf Beta",
      installerArtifactName: "SoundShelf Beta Setup.${ext}",
    },
  );
  assert.notEqual(production.appId, beta.appId);
  assert.notEqual(production.iconFileName, beta.iconFileName);
  assert.notEqual(
    production.builderOutputDirectory,
    beta.builderOutputDirectory,
  );
});

test("packaged metadata selects the immutable distribution identity", () => {
  const beta = resolveApplicationIdentity({
    isPackaged: true,
    appPath: "unused",
    environment: { SOUNDSHELF_CHANNEL: PRODUCTION_CHANNEL },
    packageMetadata: { soundShelfChannel: BETA_CHANNEL },
  });

  assert.equal(beta.productName, "SoundShelf Beta");
  assert.equal(beta.appId, "com.angelragel.soundshelf.beta");
});

test("each channel resolves a different roaming data directory", () => {
  const appDataPath = "C:\\Users\\Test\\AppData\\Roaming";
  const productionPath = resolveDefaultUserDataPath(
    appDataPath,
    getApplicationIdentity(PRODUCTION_CHANNEL),
  );
  const betaPath = resolveDefaultUserDataPath(
    appDataPath,
    getApplicationIdentity(BETA_CHANNEL),
  );

  assert.equal(productionPath, path.resolve(appDataPath, "SoundShelf"));
  assert.equal(betaPath, path.resolve(appDataPath, "SoundShelf Beta"));
  assert.notEqual(productionPath, betaPath);
});

test("database, logs, temporary files, state and icons remain channel-specific", () => {
  const productionIdentity = getApplicationIdentity(PRODUCTION_CHANNEL);
  const betaIdentity = getApplicationIdentity(BETA_CHANNEL);
  const commonOptions = {
    isPackaged: true,
    appPath: "C:\\Programs\\SoundShelf\\resources\\app.asar",
    resourcesPath: "C:\\Programs\\SoundShelf\\resources",
    platform: "win32",
    environment: {},
  };
  const production = resolveRuntimePaths({
    ...commonOptions,
    userDataPath: "C:\\Users\\Test\\AppData\\Roaming\\SoundShelf",
    identity: productionIdentity,
  });
  const beta = resolveRuntimePaths({
    ...commonOptions,
    userDataPath: "C:\\Users\\Test\\AppData\\Roaming\\SoundShelf Beta",
    identity: betaIdentity,
  });

  for (const property of [
    "databasePath",
    "logsDirectory",
    "temporaryDirectory",
    "windowStatePath",
  ]) {
    assert.notEqual(production[property], beta[property]);
  }
  assert.notEqual(
    productionIdentity.iconFileName,
    betaIdentity.iconFileName,
  );
  assert.equal(production.productName, "SoundShelf");
  assert.equal(beta.productName, "SoundShelf Beta");
});

test("builder configuration shares structure and changes channel identity", () => {
  const production = createBuilderConfiguration(PRODUCTION_CHANNEL);
  const beta = createBuilderConfiguration(BETA_CHANNEL);

  assert.equal(production.productName, "SoundShelf");
  assert.equal(production.appId, "com.angelragel.soundshelf");
  assert.equal(production.win.executableName, "SoundShelf");
  assert.equal(production.win.artifactName, "SoundShelf Setup.${ext}");
  assert.equal(production.nsis.shortcutName, "SoundShelf");
  assert.equal(production.directories.output, "release");

  assert.equal(beta.productName, "SoundShelf Beta");
  assert.equal(beta.appId, "com.angelragel.soundshelf.beta");
  assert.equal(beta.win.executableName, "SoundShelf Beta");
  assert.equal(beta.win.artifactName, "SoundShelf Beta Setup.${ext}");
  assert.equal(beta.nsis.shortcutName, "SoundShelf Beta");
  assert.equal(beta.directories.output, "release/beta");
  assert.equal(beta.extraMetadata.soundShelfChannel, BETA_CHANNEL);

  assert.notEqual(production.win.icon, beta.win.icon);
  assert.equal(
    production.extraResources.at(-1).to,
    beta.extraResources.at(-1).to,
  );
});

test("branch guard accepts only the channel allowed for the current branch", () => {
  assert.doesNotThrow(() => assertBranchAllowed(PRODUCTION_CHANNEL, "main"));
  assert.doesNotThrow(() =>
    assertBranchAllowed(BETA_CHANNEL, "feature/comparison-redesign"),
  );
  assert.throws(
    () =>
      assertBranchAllowed(PRODUCTION_CHANNEL, "feature/comparison-redesign"),
    /Production builds are only allowed from the main branch\.[\s\S]*Current branch:[\s\S]*feature\/comparison-redesign/,
  );
  assert.throws(
    () => assertBranchAllowed(BETA_CHANNEL, "main"),
    /Beta builds cannot be generated from main/,
  );
  assert.throws(
    () => assertBranchAllowed(BETA_CHANNEL, ""),
    /Distribution builds require a named branch/,
  );
});
