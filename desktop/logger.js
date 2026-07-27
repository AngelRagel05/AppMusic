"use strict";

const fs = require("node:fs");
const path = require("node:path");

class DesktopLogger {
  constructor(filePath, consoleWriter = console) {
    this.filePath = filePath;
    this.consoleWriter = consoleWriter;
    fs.mkdirSync(path.dirname(filePath), { recursive: true });
  }

  info(message) {
    this.write("INFO", message);
  }

  warn(message) {
    this.write("WARN", message);
  }

  error(message, error) {
    const details = error instanceof Error ? `\n${error.stack || error.message}` : "";
    this.write("ERROR", `${message}${details}`);
  }

  write(level, message) {
    const line = `${new Date().toISOString()} | ${level} | ${String(message)}\n`;
    fs.appendFileSync(this.filePath, line, { encoding: "utf8" });
    const writer = level === "ERROR" ? this.consoleWriter.error : this.consoleWriter.log;
    writer.call(this.consoleWriter, line.trimEnd());
  }
}

module.exports = { DesktopLogger };
