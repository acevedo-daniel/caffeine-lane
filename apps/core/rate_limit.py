from django.core.cache import cache


def client_ip(request) -> str:
    """Return the client IP address from X-Forwarded-For or REMOTE_ADDR."""
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def rate_limit_exceeded(
    *, scope: str, identity: str | int, limit: int, window: int
) -> bool:
    """Increment the counter for scope/identity and return True once limit is exceeded."""
    key = f"rate-limit:{scope}:{identity}"
    if cache.add(key, 1, timeout=window):
        count = 1
    else:
        try:
            count = cache.incr(key)
        except ValueError:
            # Key expired between cache.add() and cache.incr()
            count = 1 if cache.add(key, 1, timeout=window) else cache.incr(key)
    return count > limit
