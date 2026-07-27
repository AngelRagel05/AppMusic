"use strict";

const { getApplicationIdentity } = require("./applicationIdentity");

function createBuilderConfiguration(channel) {
  const identity = getApplicationIdentity(channel);
  const iconPath = `desktop/assets/${identity.iconFileName}`;

  return {
    appId: identity.appId,
    productName: identity.productName,
    asar: true,
    compression: "normal",
    publish: null,
    extraMetadata: {
      productName: identity.productName,
      soundShelfChannel: identity.channel,
      soundShelfAppId: identity.appId,
    },
    directories: {
      output: identity.builderOutputDirectory,
      buildResources: "desktop/assets",
    },
    files: [
      "desktop/**/*.js",
      "!desktop/tests/**",
      "!desktop/scripts/**",
      "!desktop/distributionConfiguration.js",
      "!desktop/electronBuilderConfig.js",
      "package.json",
    ],
    extraResources: [
      {
        from: "frontend/dist",
        to: "frontend",
        filter: ["**/*"],
      },
      {
        from: ".desktopBuild/backend/SoundShelfBackend",
        to: "backend",
        filter: ["**/*"],
      },
      {
        from: "node_modules/ffmpeg-static",
        to: "ffmpeg",
        filter: [
          "ffmpeg.exe",
          "ffmpeg.exe.LICENSE",
          "ffmpeg.exe.README",
          "LICENSE",
        ],
      },
      {
        from: iconPath,
        to: "icon/applicationIcon.png",
      },
    ],
    win: {
      target: [
        {
          target: "nsis",
          arch: ["x64"],
        },
      ],
      icon: iconPath,
      executableName: identity.executableName,
      artifactName: identity.installerArtifactName,
    },
    nsis: {
      oneClick: false,
      perMachine: false,
      allowElevation: true,
      allowToChangeInstallationDirectory: true,
      createDesktopShortcut: "always",
      createStartMenuShortcut: true,
      shortcutName: identity.productName,
      uninstallDisplayName: identity.productName,
    },
  };
}

module.exports = { createBuilderConfiguration };
