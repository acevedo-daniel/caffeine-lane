from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from PIL import Image

from apps.accounts.forms import ProfileForm
from apps.core.image_validators import (
    MAX_IMAGE_BYTES,
    MAX_IMAGE_DIMENSION,
    validate_uploaded_image,
)


def image_upload(image_format="PNG", size=(20, 20)):
    content = BytesIO()
    Image.new("RGB", size, color="black").save(content, format=image_format)
    return SimpleUploadedFile(
        f"upload.{image_format.lower()}", content.getvalue(), content_type="image/png"
    )


class ImageUploadValidationTests(SimpleTestCase):
    def test_allows_supported_image(self):
        validate_uploaded_image(image_upload())

    def test_rejects_unsupported_format(self):
        with self.assertRaisesRegex(ValidationError, "JPEG, PNG, WEBP"):
            validate_uploaded_image(image_upload("GIF"))

    def test_profile_form_applies_the_avatar_validator(self):
        form = ProfileForm(data={}, files={"avatar": image_upload("GIF")})

        self.assertFalse(form.is_valid())
        self.assertIn(
            "Images must use one of these formats", str(form.errors["avatar"])
        )

    def test_rejects_oversized_file(self):
        upload = SimpleUploadedFile("large.jpg", b"x" * (MAX_IMAGE_BYTES + 1))

        with self.assertRaisesRegex(ValidationError, "5 MB"):
            validate_uploaded_image(upload)

    def test_rejects_excessive_dimensions(self):
        with self.assertRaisesRegex(ValidationError, str(MAX_IMAGE_DIMENSION)):
            validate_uploaded_image(image_upload(size=(MAX_IMAGE_DIMENSION + 1, 1)))
