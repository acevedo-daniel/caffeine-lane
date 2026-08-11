from django.core.management.base import BaseCommand, CommandError
from django.db import connection


class Command(BaseCommand):
    help = "Abort if this database belongs to the legacy auth.User + Profile baseline."

    def handle(self, *args, **options):
        table_names = set(connection.introspection.table_names())
        if "accounts_profile" in table_names:
            raise CommandError(
                "This database belongs to the legacy main baseline (accounts_profile "
                "exists). This branch uses a custom accounts.User model and requires "
                "a fresh database. Create a new database or reset the local database "
                "before running migrations."
            )

        self.stdout.write("Fresh-baseline database check passed.")
