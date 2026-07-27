"use strict";

const {
  createBuilderConfiguration,
} = require("./distributionConfiguration");

const channel = process.env.SOUNDSHELF_DISTRIBUTION_CHANNEL;

if (!channel) {
  throw new Error(
    "SOUNDSHELF_DISTRIBUTION_CHANNEL is required to package SoundShelf.",
  );
}

module.exports = createBuilderConfiguration(channel);
