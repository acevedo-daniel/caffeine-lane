import { spawnSync } from "node:child_process";

const databaseUrl = process.env.E2E_DATABASE_URL || process.env.DATABASE_URL;
const command = [
  "from apps.accounts.models import User; from apps.posts.models import Comment, Post; " +
    "user, _ = User.objects.get_or_create(email='e2e-rider@example.test', defaults={'username': 'e2e-rider', 'display_name': 'E2E Rider'}); " +
    "user.set_password('e2e-rider-password'); user.save(); " +
    "post = Post.objects.get(slug='cafe-racer-de-garaje'); " +
    "Comment.objects.get_or_create(post=post, author=user, content='E2E smoke comment')",
];

const result = spawnSync(
  "uv",
  ["run", "python", "manage.py", "shell", "-c", command],
  {
    cwd: process.cwd(),
    env: {
      ...process.env,
      DJANGO_SETTINGS_MODULE: "config.settings.local",
      ...(databaseUrl ? { DATABASE_URL: databaseUrl } : {}),
      DEBUG_TOOLBAR_ENABLED: "false",
    },
    stdio: "inherit",
  },
);

if (result.error) {
  throw result.error;
}

process.exit(result.status ?? 1);
