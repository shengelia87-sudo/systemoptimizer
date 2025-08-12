import re, collections
WORD_RE = re.compile(r'[A-Za-z0-9\-_\u10A0-\u10FF\u2D00-\u2D2F\u1C90-\u1CBF]+')
SKILL_META = {'description':'Computes 64-bit simhash-like hex (poly hash)'}
def _h64(s):
    h = 1469598103934665603
    for ch in s:
        h ^= ord(ch)
        h = (h * 1099511628211) & ((1<<64)-1)
    return h
def _simhash64(tokens):
    v=[0]*64
    for t,w in collections.Counter(tokens).items():
        h=_h64(t)
        for i in range(64): v[i]+= (1 if ((h>>i)&1) else -1)*w
    out=0
    for i in range(64):
        if v[i]>0: out|=(1<<i)
    return out
def simhash_fingerprint(text=None, **kw):
    text = text or ''
    toks = [w.lower() for w in WORD_RE.findall(text)]
    h = _simhash64(toks)
    return {'ok': True, 'simhash_hex': f'{h:016x}'}
SKILLS = {'simhash_fingerprint': simhash_fingerprint}
