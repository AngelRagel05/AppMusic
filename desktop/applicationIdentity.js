"use strict";

const fs = require("node:fs");
const path = require("node:path");

const PRODUCTION_CHANNEL = "production";
const BETA_CHANNEL = "beta";

const APPLICATION_IDENTITIES = Object.freeze({
  [PRODUCTION_CHANNEL]: Object.freeze({
    channel: PRODUCTION_CHANNEL,
    productName: "SoundShelf",
    windowTitle: "SoundShelf",
    appId: "com.angelragel.soundshelf",
    executableName: "SoundShelf",
    installerArtifactName: "SoundShelf Setup.${ext}",
    userDataDirectoryName: "SoundShelf",
    iconFileName: "soundShelfIcon.png",
    builderOutputDirectory: "release",
  }),
  [BETA_CHANNEL]: Object.freeze({
    channel: BETA_CHANNEL,
    productName: "SoundShelf Beta",
    windowTitle: "SoundShelf Beta",
    appId: "com.angelragel.soundshelf.beta",
    executableName: "SoundShelf Beta",
    installerArtifactName: "SoundShelf Beta Setup.${ext}",
    userDataDirectoryName: "SoundShelf Beta",
    iconFileName: "soundShelfBetaIcon.png",
    builderOutputDirectory: "release/beta",
  }),
});

function getApplicationIdentity(channel) {
  const identity = APPLICATION_IDENTITIES[channel];
  if (!identity) {
    throw new Error(
      `Canal de distribucion desconocido: ${channel || "(vacio)"}.`,
    );
  }
  return identity;
}

function readPackagedMetadata(appPath) {
  const packagePath = path.join(appPath, "package.json");
  return JSON.parse(fs.readFileSync(packagePath, { encoding: "utf8" }));
}

function resolveApplicationIdentity({
  isPackaged,
  appPath,
  environment = process.env,
  packageMetadata = null,
}) {
  if (!isPackaged) {
    return getApplicationIdentity(
      environment.SOUNDSHELF_CHANNEL || PRODUCTION_CHANNEL,
    );
  }

  const metadata = packageMetadata || readPackagedMetadata(appPath);
  if (!metadata.soundShelfChannel) {
    throw new Error(
      "El paquete de SoundShelf no declara su canal de distribucion.",
    );
  }
  return getApplicationIdentity(metadata.soundShelfChannel);
}

function resolveDefaultUserDataPath(appDataPath, identity) {
  return path.join(
    path.resolve(appDataPath),
    identity.userDataDirectoryName,
  );
}

module.exports = {
  APPLICATION_IDENTITIES,
  BETA_CHANNEL,
  PRODUCTION_CHANNEL,
  getApplicationIdentity,
  resolveApplicationIdentity,
  resolveDefaultUserDataPath,
};
