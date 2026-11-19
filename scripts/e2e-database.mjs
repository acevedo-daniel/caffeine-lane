// Resolves the database used by the Playwright suite. E2E runs write users and
// comments, so they never inherit DATABASE_URL (which .env may point at a hosted
// database): they use E2E_DATABASE_URL or an isolated SQLite file.
export const DEFAULT_E2E_DATABASE_URL = "sqlite:///tmp/e2e.sqlite3";

const LOCAL_HOSTS = new Set(["localhost", "127.0.0.1", "[::1]"]);

export function resolveE2eDatabaseUrl(env = process.env) {
  const url = env.E2E_DATABASE_URL || DEFAULT_E2E_DATABASE_URL;
  if (url.startsWith("sqlite:")) return url;

  let host = null;
  try {
    const parsed = new URL(url);
    if (parsed.protocol.startsWith("postgres")) host = parsed.hostname;
  } catch {
    host = null;
  }
  if (host && LOCAL_HOSTS.has(host)) return url;

  throw new Error(
    "E2E_DATABASE_URL must point to SQLite or a local PostgreSQL database; " +
      "end-to-end tests write data and never run against hosted databases.",
  );
}
