from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.posts.models import BUILD_SPEC_KEYS
from apps.tests.factories import CategoryFactory, PostFactory, UserFactory


class PostBuildSpecsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = UserFactory(username="specs-author")
        cls.builds = CategoryFactory(name="Builds")

    def test_build_spec_rows_follow_canonical_key_order(self):
        post = PostFactory(
            title="Ordered build",
            author=self.author,
            categories=self.builds,
            build_specs={
                "exhaust": "Megáfono acero",
                "donor": "Honda CB750",
                "carburetor": "Keihin 28 mm",
                "displacement": "736 cc",
            },
        )

        self.assertEqual(
            post.build_spec_rows,
            [
                ("donor", "Honda CB750"),
                ("displacement", "736 cc"),
                ("carburetor", "Keihin 28 mm"),
                ("exhaust", "Megáfono acero"),
            ],
        )
        self.assertEqual(
            [key for key, _ in post.build_spec_rows],
            [key for key in BUILD_SPEC_KEYS if key in post.build_specs],
        )

    def test_full_clean_rejects_invalid_build_specs(self):
        invalid_cases = [
            (["donor"], "non-dict list"),
            ("donor: CB750", "non-dict string"),
            (None, "none"),
            ({"engine": "750 cc"}, "unknown key"),
            ({"donor": ""}, "empty value"),
            ({"donor": "   "}, "whitespace value"),
            ({"displacement": 750}, "non-string value"),
        ]

        for payload, label in invalid_cases:
            with self.subTest(case=label):
                post = PostFactory.build(
                    title="Invalid specs",
                    author=self.author,
                    build_specs=payload,
                )
                with self.assertRaises(ValidationError) as ctx:
                    post.full_clean()
                self.assertIn("build_specs", ctx.exception.error_dict)

    def test_post_detail_renders_specs_inspector_only_when_specs_exist(self):
        with_specs = PostFactory(
            title="Build with specs",
            author=self.author,
            categories=self.builds,
            build_specs={
                "donor": "Yamaha SR500",
                "exhaust": "SuperTrapp acero",
            },
        )
        without_specs = PostFactory(
            title="Build without specs",
            author=self.author,
            categories=self.builds,
        )

        with_response = self.client.get(with_specs.get_absolute_url())
        self.assertContains(with_response, "build-specs-inspector")
        self.assertContains(with_response, "Yamaha SR500")
        self.assertContains(with_response, "SuperTrapp acero")

        without_response = self.client.get(without_specs.get_absolute_url())
        self.assertNotContains(without_response, "build-specs-inspector")
