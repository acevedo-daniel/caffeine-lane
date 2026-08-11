import { cp, mkdir, rm } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const repositoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");

export const javascriptSourceDirectory = resolve(repositoryRoot, "static/src/js");
export const javascriptOutputDirectory = resolve(repositoryRoot, "static/dist/js");

/** Build a clean JavaScript output tree from the authored source tree. */
export async function buildJavaScriptAssets({
  sourceDirectory = javascriptSourceDirectory,
  outputDirectory = javascriptOutputDirectory,
} = {}) {
  await rm(outputDirectory, { recursive: true, force: true });
  await mkdir(dirname(outputDirectory), { recursive: true });
  await cp(sourceDirectory, outputDirectory, { recursive: true });
}

const invokedDirectly = process.argv[1]
  && resolve(process.argv[1]) === fileURLToPath(import.meta.url);

if (invokedDirectly) await buildJavaScriptAssets();
