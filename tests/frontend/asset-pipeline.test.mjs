import assert from "node:assert/strict";
import test from "node:test";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import { join } from "node:path";

import { buildJavaScriptAssets } from "../../scripts/build-assets.mjs";
import { watchJavaScriptAssets } from "../../scripts/dev-assets.mjs";

const waitFor = async (callback, timeoutMs = 5000) => {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (await callback()) return;
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
  throw new Error("Timed out waiting for the generated asset to update.");
};

const createFixture = async () => {
  const root = await mkdtemp(join(os.tmpdir(), "caffeine-assets-"));
  const sourceDirectory = join(root, "src", "js");
  const outputDirectory = join(root, "dist", "js");
  await mkdir(sourceDirectory, { recursive: true });
  await writeFile(join(sourceDirectory, "home-carousel.js"), "export const version = 'one';\n");
  return { outputDirectory, root, sourceDirectory };
};

test("the JavaScript build mirrors source changes and removes stale output", async () => {
  const fixture = await createFixture();
  try {
    await mkdir(fixture.outputDirectory, { recursive: true });
    await writeFile(join(fixture.outputDirectory, "obsolete.js"), "old output\n");

    await buildJavaScriptAssets(fixture);
    assert.equal(
      await readFile(join(fixture.outputDirectory, "home-carousel.js"), "utf8"),
      "export const version = 'one';\n",
    );
    await assert.rejects(readFile(join(fixture.outputDirectory, "obsolete.js"), "utf8"));

    await writeFile(join(fixture.sourceDirectory, "home-carousel.js"), "export const version = 'two';\n");
    await buildJavaScriptAssets(fixture);
    assert.equal(
      await readFile(join(fixture.outputDirectory, "home-carousel.js"), "utf8"),
      "export const version = 'two';\n",
    );
  } finally {
    await rm(fixture.root, { force: true, recursive: true });
  }
});

test("the JavaScript development watcher rebuilds output after a source edit", async () => {
  const fixture = await createFixture();
  const watcher = watchJavaScriptAssets(fixture);
  try {
    await buildJavaScriptAssets(fixture);
    await watcher.ready;
    await writeFile(join(fixture.sourceDirectory, "home-carousel.js"), "export const version = 'watched';\n");

    await waitFor(async () => {
      try {
        return (await readFile(join(fixture.outputDirectory, "home-carousel.js"), "utf8"))
          === "export const version = 'watched';\n";
      } catch {
        return false;
      }
    });
  } finally {
    await watcher.close();
    await rm(fixture.root, { force: true, recursive: true });
  }
});
