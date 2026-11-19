import assert from "node:assert/strict";
import test from "node:test";

import { DEFAULT_E2E_DATABASE_URL, resolveE2eDatabaseUrl } from "../../scripts/e2e-database.mjs";

test("defaults to the isolated SQLite database and ignores DATABASE_URL", () => {
  const url = resolveE2eDatabaseUrl({
    DATABASE_URL: "postgresql://user:secret@ep-example.us-east-2.aws.neon.tech/neondb",
  });

  assert.equal(url, DEFAULT_E2E_DATABASE_URL);
  assert.match(url, /^sqlite:\/\/\/tmp\//);
});

test("accepts an explicit SQLite database", () => {
  const url = resolveE2eDatabaseUrl({ E2E_DATABASE_URL: "sqlite:////tmp/caffeine-lane-e2e.sqlite3" });

  assert.equal(url, "sqlite:////tmp/caffeine-lane-e2e.sqlite3");
});

test("accepts a PostgreSQL database on the local machine", () => {
  for (const host of ["localhost", "127.0.0.1"]) {
    const url = `postgresql://caffeine-lane:caffeine-lane@${host}:5432/caffeine-lane`;
    assert.equal(resolveE2eDatabaseUrl({ E2E_DATABASE_URL: url }), url);
  }
});

test("refuses a remote database without echoing its credentials", () => {
  assert.throws(
    () =>
      resolveE2eDatabaseUrl({
        E2E_DATABASE_URL: "postgresql://user:secret@ep-example.us-east-2.aws.neon.tech/neondb",
      }),
    (error) => {
      assert.match(error.message, /E2E_DATABASE_URL must point to SQLite or a local PostgreSQL/);
      assert.doesNotMatch(error.message, /secret|neon\.tech/);
      return true;
    },
  );
});
