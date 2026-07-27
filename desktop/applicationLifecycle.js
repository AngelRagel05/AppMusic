"use strict";

function focusExistingWindow(window) {
  if (!window || window.isDestroyed()) {
    return;
  }
  if (window.isMinimized()) {
    window.restore();
  }
  window.show();
  window.focus();
}

function acquireSingleInstance(app, getWindow) {
  if (!app.requestSingleInstanceLock()) {
    app.quit();
    return false;
  }
  app.on("second-instance", () => {
    focusExistingWindow(getWindow());
  });
  return true;
}

module.exports = { acquireSingleInstance, focusExistingWindow };
