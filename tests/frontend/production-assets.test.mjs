import assert from "node:assert/strict";
import { readdir, readFile, stat } from "node:fs/promises";
import { dirname, join, relative } from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const repositoryRoot = join(dirname(fileURLToPath(import.meta.url)), "../..");
const sourceDirectory = join(repositoryRoot, "static", "src");
const outputDirectory = join(repositoryRoot, "static", "dist");

async function filesRecursively(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const nested = await Promise.all(entries.map(async (entry) => {
    const path = join(directory, entry.name);
    return entry.isDirectory() ? filesRecursively(path) : [path];
  }));
  return nested.flat();
}

test("production asset output contains compiled CSS and every authored JavaScript module", async () => {
  const cssOutput = join(outputDirectory, "css", "app.css");
  const cssMetadata = await stat(cssOutput);
  assert.ok(cssMetadata.size > 0, "compiled CSS must not be empty");

  const javascriptSources = await filesRecursively(join(sourceDirectory, "js"));
  assert.ok(javascriptSources.length > 0, "at least one JavaScript source file is expected");

  await Promise.all(javascriptSources.map(async (sourcePath) => {
    const outputPath = join(outputDirectory, relative(sourceDirectory, sourcePath));
    const [source, output] = await Promise.all([
      readFile(sourcePath, "utf8"),
      readFile(outputPath, "utf8"),
    ]);
    assert.equal(
      output,
      source,
      `${relative(sourceDirectory, sourcePath)} is stale in static/dist`,
    );
  }));
});
