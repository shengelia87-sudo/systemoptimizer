import re
import statistics

SKILL_META = {"description": "Extracts numbers and returns basic stats (auto-generated)"}


def number_stats(text=None, **kw):
    nums = [
        float(x)
        for x in re.findall(
            r"(?<!\d{4}-)(?<!-\d-)(?<!-\d{2}-)(?<!\d)[-+]?\d+(?:\.\d+)?(?!\d)", text or ""
        )
    ]
    if not nums:
        return {"ok": True, "count": 0}
    return {
        "ok": True,
        "count": len(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": statistics.mean(nums),
        "median": statistics.median(nums),
    }


SKILLS = {"number_stats": number_stats}
