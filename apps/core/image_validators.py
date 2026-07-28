from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_IMAGE_DIMENSION = 5000


def validate_uploaded_image(upload):
    # Existing files were validated when uploaded; validators receive a FieldFile
    # during model validation and must not reopen storage just to validate its name.
    if getattr(upload, "_committed", False):
        return

    if upload.size > MAX_IMAGE_BYTES:
        raise ValidationError("Images must be 5 MB or smaller.", code="image_too_large")

    try:
        image = Image.open(upload)
        image.verify()
    except (UnidentifiedImageError, OSError, ValueError) as error:
        raise ValidationError(
            "Upload a valid image file.", code="invalid_image"
        ) from error
    finally:
        upload.seek(0)

    if image.format not in ALLOWED_IMAGE_FORMATS:
        allowed_formats = ", ".join(sorted(ALLOWED_IMAGE_FORMATS))
        raise ValidationError(
            f"Images must use one of these formats: {allowed_formats}.",
            code="unsupported_image_format",
        )

    if max(image.size) > MAX_IMAGE_DIMENSION:
        raise ValidationError(
            f"Images must be at most {MAX_IMAGE_DIMENSION} pixels on either side.",
            code="image_dimensions_too_large",
        )
