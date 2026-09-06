from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(LANGUAGE_CODE="es", DEBUG=False)
class InternationalizationTests(TestCase):
    def test_default_visit_renders_spanish_by_default(self):
        """Initial visitor without language cookie receives Spanish by default."""
        response = self.client.get("/home/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn('lang="es"', content)
        self.assertIn("Historias para la ruta.", content)

    def test_default_landing_renders_spanish_by_default(self):
        """Landing page renders Spanish copy and lang="es" on cold visit."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn('lang="es"', content)
        self.assertIn("HONESTIDAD HECHA A MANO. CULTURA CAFÉ RACER CURADA.", content)

    def test_set_language_to_english_and_preserves_next_url(self):
        """Switching to English sets cookie and switches language in subsequent requests."""
        set_language_url = reverse("set_language")
        response = self.client.post(
            set_language_url,
            data={"language": "en", "next": "/home/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/home/")
        self.assertIn("django_language", response.cookies)
        self.assertEqual(response.cookies["django_language"].value, "en")

        # Request /home/ with English cookie
        response = self.client.get("/home/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn('lang="en"', content)
        self.assertIn("Stories for the road.", content)

    def test_switch_back_to_spanish(self):
        """User can switch from English back to Spanish cleanly."""
        self.client.cookies.load({"django_language": "en"})
        response = self.client.get("/about/")
        self.assertIn('lang="en"', response.content.decode("utf-8"))

        set_language_url = reverse("set_language")
        post_response = self.client.post(
            set_language_url,
            data={"language": "es", "next": "/about/"},
        )
        self.assertEqual(post_response.status_code, 302)
        self.assertEqual(post_response["Location"], "/about/")

        response = self.client.get("/about/")
        self.assertIn('lang="es"', response.content.decode("utf-8"))

    def test_both_desktop_and_mobile_language_switchers_are_present(self):
        """Header contains both desktop (#language-switcher) and mobile (#mobile-language-switcher) controls."""
        response = self.client.get("/home/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")

        self.assertIn('id="language-switcher"', content)
        self.assertIn('id="mobile-language-switcher"', content)
        self.assertIn('data-submit-on-change="true"', content)
        self.assertIn('aria-label="Idioma"', content)
