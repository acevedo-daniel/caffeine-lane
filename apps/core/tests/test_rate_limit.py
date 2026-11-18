from unittest.mock import patch

from django.core.cache import cache
from django.test import RequestFactory, SimpleTestCase

from apps.core.rate_limit import client_ip, rate_limit_exceeded


class RateLimitHelperTests(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.factory = RequestFactory()

    def test_client_ip_prefers_first_forwarded_for_entry_over_remote_addr(self):
        forwarded_request = self.factory.post(
            "/contact/",
            HTTP_X_FORWARDED_FOR="203.0.113.10, 198.51.100.2",
            REMOTE_ADDR="127.0.0.1",
        )
        direct_request = self.factory.post("/contact/", REMOTE_ADDR="198.51.100.7")

        self.assertEqual(client_ip(forwarded_request), "203.0.113.10")
        self.assertEqual(client_ip(direct_request), "198.51.100.7")

    def test_rate_limit_exceeded_allows_limit_hits_then_blocks(self):
        for _ in range(3):
            self.assertFalse(
                rate_limit_exceeded(
                    scope="login",
                    identity="192.0.2.1",
                    limit=3,
                    window=60,
                )
            )

        self.assertTrue(
            rate_limit_exceeded(
                scope="login",
                identity="192.0.2.1",
                limit=3,
                window=60,
            )
        )

    def test_rate_limit_scopes_and_identities_are_independent(self):
        for _ in range(2):
            self.assertFalse(
                rate_limit_exceeded(
                    scope="login",
                    identity="192.0.2.1",
                    limit=2,
                    window=60,
                )
            )
        self.assertTrue(
            rate_limit_exceeded(
                scope="login",
                identity="192.0.2.1",
                limit=2,
                window=60,
            )
        )

        # Different scope with the same identity is unaffected
        self.assertFalse(
            rate_limit_exceeded(
                scope="register",
                identity="192.0.2.1",
                limit=2,
                window=60,
            )
        )
        # Different identity in the same scope is unaffected
        self.assertFalse(
            rate_limit_exceeded(
                scope="login",
                identity="192.0.2.2",
                limit=2,
                window=60,
            )
        )

    def test_rate_limit_exceeded_recovers_when_key_expires_before_incr(self):
        with (
            patch.object(cache, "add", side_effect=[False, True]) as mock_add,
            patch.object(cache, "incr", side_effect=ValueError("expired")),
        ):
            blocked = rate_limit_exceeded(
                scope="comment",
                identity="42",
                limit=5,
                window=600,
            )

        self.assertFalse(blocked)
        self.assertEqual(mock_add.call_count, 2)
