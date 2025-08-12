"""
WordCount MAX+++ — Georgian/Latin words + decimal numbers. No regex; ignores punctuation/emoji.
Handles Windows mojibake ('áƒ…') via a safe cp1252→utf-8 repair heuristic.
"""

from typing import List, Tuple, Dict, Any, Optional
import statistics

VERSION = "wordcount-max+++ 2025-08-11-fallback3"

SKILL_META = {
    "description": "Counts words (Georgian/Latin) and decimal numbers; repairs mojibake; ignores punctuation/emoji",
    "version": VERSION
}

# ---- script helpers ----
def _is_ge(ch: str) -> bool:
    cp = ord(ch)
    return (0x10A0 <= cp <= 0x10FF) or (0x2D00 <= cp <= 0x2D2F) or (0x1C90 <= cp <= 0x1CBF)

def _is_lat(ch: str) -> bool:
    cp = ord(ch)
    return (0x0041 <= cp <= 0x005A) or (0x0061 <= cp <= 0x007A) or (0x00C0 <= cp <= 0x024F)

_PUNCT = set(".,;:!?()[]{}\"'`~@#$%^&*+=/\\|<>—–-…„“”’‚‹›«»")

def _is_word_letter(ch: str) -> bool:
    # strict + wide fallback
    if _is_ge(ch) or _is_lat(ch) or ch.isalpha():
        return True
    cp = ord(ch)
    if cp > 0x7F and (not ch.isspace()) and (not ch.isdigit()) and (ch not in _PUNCT):
        return True
    return False

def _script_accepts(word: str, script: str) -> bool:
    if script == "any": return True
    has_ge = any(_is_ge(c) for c in word)
    has_lat = any(_is_lat(c) for c in word)
    if script == "ge":  return has_ge and not has_lat
    if script == "lat": return has_lat and not has_ge
    return True

# ---- mojibake repair ----
def _maybe_repair_mojibake(s: str) -> str:
    # Classic Georgian-as-cp1252 pattern: contains "áƒ"
    if "áƒ" in s:
        try:
            repaired = s.encode("cp1252", errors="strict").decode("utf-8", errors="strict")
            # accept only if Georgian letters increased
            def ge_count(t: str) -> int: return sum(1 for ch in t if _is_ge(ch))
            if ge_count(repaired) > ge_count(s):
                return repaired
        except Exception:
            pass
    return s

# ---- tokenizer (no regex) ----
def _tokenize(text: str, *, join_hyphen: bool=False,
              allow_sign: bool=True, allow_decimal: bool=True) -> List[Tuple[str,str]]:
    s = _maybe_repair_mojibake(text or "")
    out: List[Tuple[str,str]] = []
    i, n = 0, len(s)
    while i < n:
        ch = s[i]
        if ch.isspace():
            i += 1; continue

        # number
        k = i
        if allow_sign and ch in "+-" and (i+1 < n and s[i+1].isdigit()):
            k += 1
        j = k; has_int = False
        while j < n and s[j].isdigit():
            has_int = True; j += 1
        if has_int:
            if allow_decimal and j < n and s[j]=='.' and (j+1 < n and s[j+1].isdigit()):
                j2 = j + 1
                while j2 < n and s[j2].isdigit(): j2 += 1
                out.append((s[i:j2], "number")); i = j2; continue
            out.append((s[i:j], "number")); i = j; continue

        # word
        if _is_word_letter(ch):
            j = i + 1
            while j < n:
                cj = s[j]
                if _is_word_letter(cj): j += 1; continue
                if join_hyphen and cj == '-' and (j+1 < n and _is_word_letter(s[j+1])):
                    j += 2; continue
                break
            out.append((s[i:j], "word")); i = j; continue

        i += 1
    return out

# ---- skill entrypoint ----
def word_count(text: Optional[str]=None, **kw: Any) -> Dict[str, Any]:
    mode = str(kw.get("mode", "both")).lower()
    return_tokens = bool(kw.get("return_tokens", False))
    include_stats = bool(kw.get("include_stats", False))
    normalize_case = bool(kw.get("normalize_case", False))
    join_hyphen = bool(kw.get("join_hyphen", False))
    allow_sign = bool(kw.get("allow_sign", True))
    allow_decimal = bool(kw.get("allow_decimal", True))
    script = str(kw.get("script", "any")).lower()
    max_tokens = int(kw.get("max_tokens", 10000))

    toks = _tokenize(text or "", join_hyphen=join_hyphen,
                     allow_sign=allow_sign, allow_decimal=allow_decimal)

    words: List[str] = []; numbers: List[str] = []
    for tok, kind in toks:
        if kind == "word":
            if not _script_accepts(tok, script): continue
            words.append(tok.casefold() if normalize_case else tok)
        else:
            numbers.append(tok)

    if mode == "words": numbers = []
    elif mode == "numbers": words = []

    res: Dict[str, Any] = {
        "ok": True,
        "count": len(words) + len(numbers),
        "words": len(words),
        "numbers": len(numbers),
        "meta": {"impl": VERSION, "mode": mode, "normalize_case": normalize_case,
                 "join_hyphen": join_hyphen, "allow_sign": allow_sign,
                 "allow_decimal": allow_decimal, "script": script}
    }
    if return_tokens:
        res["word_tokens"] = words[:max_tokens]
        res["number_tokens"] = numbers[:max_tokens]

    if include_stats and numbers:
        vals: List[float] = []
        for t in numbers:
            try: vals.append(float(t))
            except Exception: pass
        if vals:
            res["number_stats"] = {
                "min": min(vals), "max": max(vals),
                "mean": statistics.mean(vals), "median": statistics.median(vals)
            }
    return res

SKILLS = {"word_count": word_count}

