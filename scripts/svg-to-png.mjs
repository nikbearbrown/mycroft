#!/usr/bin/env node
import { glob } from "glob";
import sharp from "sharp";
import { stat } from "node:fs/promises";
import path from "node:path";

const svgs = await glob("images/**/*.svg");
for (const svg of svgs) {
  const png = svg.replace(/\.svg$/i, ".png");
  let skip = false;
  try {
    const [src, out] = await Promise.all([stat(svg), stat(png)]);
    skip = out.mtimeMs >= src.mtimeMs;
  } catch {}
  if (skip) continue;
  await sharp(svg, { density: 300 }).png().toFile(png);
  console.log(`${svg} -> ${png}`);
}
if (!svgs.length) console.log("No SVG files found under images/.");
