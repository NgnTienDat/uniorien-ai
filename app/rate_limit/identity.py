import hashlib
from fastapi import Request

COOKIE_NAME = "uniorien_fp"


def resolve_fingerprint(request: Request) -> str:
    ip = request.client.host if request.client else "unknown" # Get client IP address
    ua = request.headers.get("user-agent", "unknown")   # Get User-Agent header

    print("IP:", ip)
    print("User-Agent:", ua)

    cookie_fp = request.cookies.get(COOKIE_NAME)
    if not cookie_fp:
        raw = f"{ip}:{ua}"
        cookie_fp = hashlib.sha256(raw.encode()).hexdigest()

    raw_fp = f"{ip}:{ua}:{cookie_fp}"
    fingerprint = hashlib.sha256(raw_fp.encode()).hexdigest()

    return fingerprint
