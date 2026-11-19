import { spawnSync } from "node:child_process";
import { mkdirSync } from "node:fs";

import { resolveE2eDatabaseUrl } from "./e2e-database.mjs";

const databaseUrl = resolveE2eDatabaseUrl();
mkdirSync("tmp", { recursive: true });

const env = {
  ...process.env,
  DJANGO_SETTINGS_MODULE: "config.settings.local",
  DATABASE_URL: databaseUrl,
  DEBUG_TOOLBAR_ENABLED: "false",
};

const seedFixtures =
  "from django.core.management import call_command; " +
  "from django.contrib.auth.models import Permission; " +
  "from apps.accounts.models import User; from apps.posts.models import Comment, Post; " +
  "Post.objects.filter(slug='cafe-racer-de-garaje').exists() or call_command('seed_editorial'); " +
  "user, _ = User.objects.get_or_create(email='e2e-rider@example.test', defaults={'username': 'e2e-rider', 'display_name': 'E2E Rider'}); " +
  "user.set_password('e2e-rider-password'); user.save(); " +
  "post = Post.objects.get(slug='cafe-racer-de-garaje'); " +
  "comment, _ = Comment.objects.get_or_create(post=post, author=user, parent=None, defaults={'content': 'E2E smoke comment'}); " +
  "editor, _ = User.objects.get_or_create(email='e2e-editor@example.test', defaults={'username': 'e2e-editor', 'display_name': 'E2E Editor'}); " +
  "editor.set_password('e2e-editor-password'); editor.is_staff = True; editor.save(); " +
  "editor.user_permissions.add(Permission.objects.get(codename='delete_post', content_type__app_label='posts')); " +
  "Comment.objects.get_or_create(post=post, author=editor, parent=comment, defaults={'content': 'E2E smoke reply'})";

for (const args of [
  ["manage.py", "migrate", "--noinput"],
  ["manage.py", "shell", "-c", seedFixtures],
]) {
  const result = spawnSync("uv", ["run", "python", ...args], {
    cwd: process.cwd(),
    env,
    stdio: "inherit",
  });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status ?? 1);
}
