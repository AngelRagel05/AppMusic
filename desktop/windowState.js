"use strict";

const fs = require("node:fs");
const path = require("node:path");

const MINIMUM_WIDTH = 1024;
const MINIMUM_HEIGHT = 680;

function intersectsDisplay(bounds, displays) {
  return displays.some(({ workArea }) => {
    const intersectionWidth = Math.max(
      0,
      Math.min(bounds.x + bounds.width, workArea.x + workArea.width) -
        Math.max(bounds.x, workArea.x),
    );
    const intersectionHeight = Math.max(
      0,
      Math.min(bounds.y + bounds.height, workArea.y + workArea.height) -
        Math.max(bounds.y, workArea.y),
    );
    return intersectionWidth >= 100 && intersectionHeight >= 100;
  });
}

function readWindowState(filePath, displays) {
  try {
    const parsedState = JSON.parse(fs.readFileSync(filePath, "utf8"));
    const bounds = {
      x: Number(parsedState.x),
      y: Number(parsedState.y),
      width: Math.max(MINIMUM_WIDTH, Number(parsedState.width)),
      height: Math.max(MINIMUM_HEIGHT, Number(parsedState.height)),
    };
    if (
      Object.values(bounds).every(Number.isFinite) &&
      intersectsDisplay(bounds, displays)
    ) {
      return bounds;
    }
  } catch {
    return null;
  }
  return null;
}

function writeWindowState(filePath, bounds) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  const temporaryPath = `${filePath}.tmp`;
  fs.writeFileSync(temporaryPath, JSON.stringify(bounds), "utf8");
  fs.renameSync(temporaryPath, filePath);
}

module.exports = {
  MINIMUM_HEIGHT,
  MINIMUM_WIDTH,
  readWindowState,
  writeWindowState,
};
