import re
import unicodedata
from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.dateparse import parse_datetime

PROVISIONAL_TEXT_MARKERS = ("lorem ipsum", "todo", "tbd", "placeholder")


def clean_text(value, *, field):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError({field: "A non-empty text value is required."})

    value = unicodedata.normalize("NFC", value).replace("\r\n", "\n").strip()
    if "\ufffd" in value or any(
        ord(char) < 32 and char not in "\n\t" for char in value
    ):
        raise ValidationError(
            {field: "The text contains invalid encoding or control characters."}
        )
    if any(
        re.search(rf"\b{re.escape(marker)}\b", value, flags=re.IGNORECASE)
        for marker in PROVISIONAL_TEXT_MARKERS
    ):
        raise ValidationError({field: "Provisional text is not importable."})
    return value


def parse_published_at(value):
    if isinstance(value, datetime):
        return value
    parsed = parse_datetime(value) if isinstance(value, str) else None
    if parsed is None:
        raise ValidationError({"published_at": "Use an ISO 8601 datetime."})
    if timezone.is_naive(parsed):
        parsed = timezone.make_aware(parsed)
    return parsed
