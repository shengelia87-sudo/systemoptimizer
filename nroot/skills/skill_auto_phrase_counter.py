import re, collections
SKILL_META = {'description':'Counts given phrases in text (auto-generated)'}
_PHRASES = ["price", "price 2025-08-11", "price 2025-08-11 https", "2025-08-11", "2025-08-11 https", "2025-08-11 https example", "https", "https example", "https example com", "example"]
def phrase_counter(text=None, phrases=None, **kw):
    terms = [w.lower() for w in re.findall(r'[A-Za-z0-9\-_\u10A0-\u10FF\u2D00-\u2D2F\u1C90-\u1CBF]+', text or '')]
    want = [w.lower() for w in (phrases or _PHRASES)]
    c = collections.Counter(terms)
    return {'ok': True, 'counts': {w: c.get(w, 0) for w in want}}
SKILLS = {'phrase_counter': phrase_counter}
