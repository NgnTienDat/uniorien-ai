from app.rate_limit.store import get_used_tokens, incr_tokens

TOKEN_LIMIT = 12_000


def estimate_tokens(request) -> int:
    """
    Phase 1: estimate thô, chưa cần tokenizer.
    """
    query_length = len(request.query or "")
    base_cost = 2_300  # upper bound pipeline
    return base_cost + int(query_length * 0.5)


def check_rate_limit(fingerprint: str, request) -> bool:
    redis_key = f"uniorien:quota:{fingerprint}"

    estimated_tokens = estimate_tokens(request)
    used_tokens = get_used_tokens(redis_key)

    if used_tokens + estimated_tokens > TOKEN_LIMIT:
        return False

    incr_tokens(redis_key, estimated_tokens)
    return True
