from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase


class FreshBaselineCheckTests(SimpleTestCase):
    def test_check_passes_without_legacy_profile_table(self):
        with patch(
            "apps.accounts.management.commands.check_fresh_baseline."
            "connection.introspection.table_names",
            return_value=[],
        ):
            call_command("check_fresh_baseline")

    def test_check_rejects_legacy_profile_table(self):
        with patch(
            "apps.accounts.management.commands.check_fresh_baseline."
            "connection.introspection.table_names",
            return_value=["accounts_profile"],
        ):
            with self.assertRaisesMessage(CommandError, "requires a fresh database"):
                call_command("check_fresh_baseline")
