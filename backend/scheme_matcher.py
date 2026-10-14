"""Match a message against the local verified-schemes database."""
import json, re
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rules import SCHEME_CLAIM

DATA = Path(__file__).parent / "data" / "schemes.json"
_schemes = json.loads(DATA.read_text(encoding="utf-8"))
_docs = [" ".join([s["name"], " ".join(s["aliases"]), " ".join(s["keywords"])]).lower() for s in _schemes]
_vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5)).fit(_docs)
_mat = _vec.transform(_docs)


def all_schemes():
    return _schemes


def _alias_hit(text_l: str):
    best, best_len = None, 0
    for s in _schemes:
        for a in s["aliases"]:
            if len(a) >= 4 and re.search(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", text_l):
                if len(a) > best_len:
                    best, best_len = s, len(a)
    return best


def match_scheme(text: str):
    """Return dict(status, scheme?, score?, claimed?)
    status: 'verified_match' | 'claimed_not_found' | 'no_scheme_claim'
    """
    t = (text or "").lower()
    hit = _alias_hit(t)
    if hit:
        return {"status": "verified_match", "score": 1.0, "scheme": hit}
    claim = SCHEME_CLAIM.search(text or "")
    if claim:
        q = _vec.transform([claim.group(0).lower()])
        sims = cosine_similarity(q, _mat)[0]
        i = int(np.argmax(sims))
        if sims[i] >= 0.55:
            return {"status": "verified_match", "score": float(sims[i]), "scheme": _schemes[i]}
        return {"status": "claimed_not_found", "claimed": claim.group(0).strip(), "score": float(sims[i])}
    return {"status": "no_scheme_claim"}
