import { spawn } from "node:child_process";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import chokidar from "chokidar";

import {
  buildJavaScriptAssets,
  javascriptOutputDirectory,
  javascriptSourceDirectory,
} from "./build-assets.mjs";

const repositoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const cssSource = "./static/src/css/app.css";
const cssOutput = "./static/dist/css/app.css";

/** Watch the authored JS tree and mirror every change to the generated tree. */
export function watchJavaScriptAssets({
  sourceDirectory = javascriptSourceDirectory,
  outputDirectory = javascriptOutputDirectory,
} = {}) {
  let timer;
  let buildQueue = Promise.resolve();
  let isClosed = false;
  let resolveReady;
  const ready = new Promise((resolveReadyPromise) => {
    resolveReady = resolveReadyPromise;
  });

  const queueBuild = () => {
    if (isClosed) return;
    clearTimeout(timer);
    timer = setTimeout(() => {
      buildQueue = buildQueue
        .then(() => buildJavaScriptAssets({ sourceDirectory, outputDirectory }))
        .then(() => console.log("JavaScript assets rebuilt."))
        .catch((error) => console.error("JavaScript asset rebuild failed.", error));
    }, 75);
  };

  const watcher = chokidar.watch(sourceDirectory, {
    awaitWriteFinish: { stabilityThreshold: 100, pollInterval: 25 },
    ignoreInitial: true,
  });

  watcher
    .on("add", queueBuild)
    .on("change", queueBuild)
    .on("unlink", queueBuild)
    .on("addDir", queueBuild)
    .on("unlinkDir", queueBuild)
    .on("ready", resolveReady);

  return {
    ready,
    async close() {
      isClosed = true;
      clearTimeout(timer);
      await watcher.close();
      await buildQueue;
    },
  };
}

async function startDevelopmentAssets({ javascriptOnly = false } = {}) {
  await buildJavaScriptAssets();
  console.log("JavaScript assets built. Watching static/src/js.");
  const javascriptWatcher = watchJavaScriptAssets();
  await javascriptWatcher.ready;

  let cssWatcher;
  if (!javascriptOnly) {
    const tailwindArguments = [
      "exec",
      "tailwindcss",
      "-i",
      cssSource,
      "-o",
      cssOutput,
      "--watch",
    ];
    const isWindows = process.platform === "win32";
    cssWatcher = spawn(
      isWindows ? (process.env.ComSpec || "cmd.exe") : "pnpm",
      isWindows
        ? ["/d", "/s", "/c", `pnpm ${tailwindArguments.join(" ")}`]
        : tailwindArguments,
      {
        cwd: repositoryRoot,
        stdio: "inherit",
      },
    );
  }

  const stopCssWatcher = async () => {
    if (!cssWatcher || cssWatcher.exitCode !== null) return;

    if (process.platform === "win32") {
      await new Promise((resolveStop) => {
        const taskkill = spawn(
          "taskkill",
          ["/pid", String(cssWatcher.pid), "/T", "/F"],
          { stdio: "ignore" },
        );
        taskkill.once("close", resolveStop);
      });
      return;
    }

    cssWatcher.kill("SIGTERM");
  };

  const stop = async () => {
    await stopCssWatcher();
    await javascriptWatcher.close();
  };
  process.once("SIGINT", stop);
  process.once("SIGTERM", stop);

  await new Promise((resolveExit) => {
    if (cssWatcher) cssWatcher.once("exit", resolveExit);
  });
  await javascriptWatcher.close();
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  await startDevelopmentAssets({ javascriptOnly: process.argv.includes("--js-only") });
}
