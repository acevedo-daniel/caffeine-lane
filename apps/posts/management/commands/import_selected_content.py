import json
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.models import User
from apps.posts.content_import import import_selected_content


class Command(BaseCommand):
    help = "Import explicitly selected editorial content from a reviewed JSON file."

    def add_arguments(self, parser):
        parser.add_argument("path", type=Path)
        parser.add_argument("--author-email", required=True)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        path = options["path"]
        if not path.is_file():
            raise CommandError(f"Import file does not exist: {path}")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise CommandError(f"Cannot read valid UTF-8 JSON: {error}") from error
        try:
            author = User.objects.get(email__iexact=options["author_email"])
        except User.DoesNotExist as error:
            raise CommandError(
                "Create the non-privileged author before importing."
            ) from error
        try:
            with transaction.atomic():
                result = import_selected_content(
                    payload, author=author, dry_run=options["dry_run"]
                )
        except ValidationError as error:
            raise CommandError(error) from error
        action = "Validated" if options["dry_run"] else "Imported"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} {result['categories']} categories and {result['posts']} posts."
            )
        )
