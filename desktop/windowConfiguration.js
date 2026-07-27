"use strict";

const { MINIMUM_HEIGHT, MINIMUM_WIDTH } = require("./windowState");

function createWindowOptions({
  bounds,
  enableDevTools,
  iconPath,
  preloadPath,
}) {
  return {
    title: "SoundShelf",
    show: false,
    width: bounds?.width || 1440,
    height: bounds?.height || 900,
    ...(bounds ? { x: bounds.x, y: bounds.y } : {}),
    minWidth: MINIMUM_WIDTH,
    minHeight: MINIMUM_HEIGHT,
    backgroundColor: "#10131c",
    autoHideMenuBar: true,
    frame: true,
    icon: iconPath,
    webPreferences: {
      preload: preloadPath,
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webSecurity: true,
      allowRunningInsecureContent: false,
      devTools: enableDevTools,
      webviewTag: false,
    },
  };
}

module.exports = { createWindowOptions };
