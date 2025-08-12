import re

SKILL_META = {"description": "Extract urls/emails/dates/numbers (or safe regex)"}
PATTERNS = {
    "url": r"https?://\S+",
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "date": r"\b(20\d{2}|19\d{2})[-/.](0?[1-9]|1[0-2])[-/.](0?[1-9]|[12]\d|3[01])\b",
    "number": r"(?<!\d{4}-)(?<!-\d-)(?<!-\d{2}-)(?<!\d)[-+]?\d+(?:\.\d+)?(?!\d)",
}


def _safe(pat):
    if pat.count("(") > 10 or pat.count("{") > 10:
        return None
    return pat


def regex_extract(text=None, mode="auto", pattern=None, **kw):
    text = text or ""
    pats = {}
    if mode == "auto":
        pats = PATTERNS
    elif mode in PATTERNS:
        pats = {mode: PATTERNS[mode]}
    elif pattern:
        sp = _safe(pattern)
        if sp:
            pats = {"custom": sp}
    out = {}
    for k, p in pats.items():
        try:
            out[k] = re.findall(p, text)[:1000]
        except Exception:
            out[k] = []
    return {"ok": True, "matches": out}


SKILLS = {"regex_extract": regex_extract}
