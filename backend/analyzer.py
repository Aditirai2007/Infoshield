"""
Core InfoShield pipeline (framework independent, so it can be unit-tested):
  text -> URL checks + rule engine + ML classifier + scheme database lookup -> verdict
"""
import json, re
from pathlib import Path
import joblib, numpy as np

import url_checker, rules, scheme_matcher

HERE = Path(__file__).parent
MODEL_PATH = HERE / "models" / "model.pkl"
METRICS_PATH = HERE / "models" / "metrics.json"

_model = None


def load_model():
    global _model
    if _model is None and MODEL_PATH.exists():
        try:
            _model = joblib.load(MODEL_PATH)
        except Exception as e:  # e.g. scikit-learn version mismatch -> retrain with: python train_model.py
            print("WARNING: could not load models/model.pkl (" + str(e)[:80] + "). Run: python train_model.py")
    return _model


def model_info():
    if METRICS_PATH.exists():
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return {"error": "Model not trained yet. Run: python train_model.py"}


def ml_probability(text: str):
    """Return (prob_fake, top_terms_pushing_towards_fake)."""
    m = load_model()
    if m is None:
        return None, []
    p = float(m.predict_proba([text])[0][1])
    terms = []
    try:
        feats = m.named_steps["features"]
        vec = feats.transform([text])
        names = feats.get_feature_names_out()
        coefs = m.named_steps["clf"].coef_[0]
        row = vec.tocoo()
        contrib = [(names[j][6:], float(v * coefs[j])) for j, v in zip(row.col, row.data) if names[j].startswith("word__")]
        contrib = [c for c in contrib if c[1] > 0.05 and len(c[0]) > 2]
        contrib.sort(key=lambda x: -x[1])
        seen = []
        for w, _ in contrib:
            if not any(w in s or s in w for s in seen):
                seen.append(w)
            if len(seen) == 5:
                break
        terms = seen
    except Exception:
        pass
    return p, terms


def _noisy_or(weights):
    prod = 1.0
    for w in weights:
        prod *= (1 - w)
    return 1 - prod


def analyze(text: str, input_type: str = "text") -> dict:
    text = (text or "").strip()
    if not text:
        return {"error": "Empty input. Paste a message, a link, or upload a screenshot."}

    urls = url_checker.check_all(text)
    flags = rules.run_rules(text, urls)
    scheme = scheme_matcher.match_scheme(text)
    ml_p, ml_terms = ml_probability(text)

    has_official = any(u["is_official"] for u in urls)
    has_bad = any(not u["is_official"] for u in urls)
    ids = {f.id for f in flags}

    # scheme database signals
    if scheme["status"] == "verified_match":
        tampered = bool(ids & {"fee_demand", "sensitive_info"}) or has_bad
        if tampered:
            flags.append(rules.Flag("tampered_claim", "Real scheme name, but unsafe details",
                                    f"The message uses the real scheme '{scheme['scheme']['name']}' but adds a fee/OTP demand or a non-government link. Real details are only on {scheme['scheme']['official_url']}.",
                                    "high", 0.35))
            ids.add("tampered_claim")
    elif scheme["status"] == "claimed_not_found":
        flags.append(rules.Flag("scheme_not_found", "Scheme not found in verified list",
                                f"\"{scheme['claimed']}\" does not match any scheme in InfoShield's verified database ({len(scheme_matcher.all_schemes())} schemes). That is not proof it is fake, but check myscheme.gov.in before trusting it.",
                                "medium", 0.18))
        ids.add("scheme_not_found")

    rule_score = _noisy_or([f.weight for f in flags])

    # combine ML and rules
    if ml_p is None:
        risk = rule_score
        engine = "rules only (ML model not trained)"
    else:
        risk = 0.5 * ml_p + 0.5 * rule_score
        engine = "ML classifier + rule engine + scheme database"

    critical = ids & {"fee_demand", "sensitive_info", "tampered_claim"}
    if critical and (has_bad or not has_official):
        risk = max(risk, 0.88)
    elif critical:
        risk = max(risk, 0.7)
    if has_official and not has_bad and not critical:
        risk = min(risk, 0.2) if rule_score < 0.3 else risk * 0.7
    if not flags and (ml_p is None or ml_p < 0.5):
        risk = min(risk, 0.3)
    risk = float(min(max(risk, 0.02), 0.99))

    if risk >= 0.65:
        verdict, label = "fake", "Likely Fake / Scam"
    elif risk >= 0.35:
        verdict, label = "verify", "Needs Verification"
    else:
        verdict, label = "genuine", "Likely Genuine"

    # chart breakdown (0..100), each bar is a real component
    def mx(ids_, default=0.0):
        ws = [f.weight for f in flags if f.id in ids_]
        return max(ws) if ws else default
    url_sev = max([u["severity"] for u in urls], default=0.0)
    if scheme["status"] == "verified_match":
        scheme_risk = 85 if "tampered_claim" in ids else 5
    elif scheme["status"] == "claimed_not_found":
        scheme_risk = 60
    else:
        scheme_risk = 25
    breakdown = {
        "labels": ["ML model", "Link / domain", "Money / OTP ask", "Urgency & chain tactics", "Scheme database"],
        "values": [round((ml_p if ml_p is not None else rule_score) * 100), round(url_sev * 100),
                   round(mx({"fee_demand", "sensitive_info"}) / 0.5 * 100), round(mx({"urgency", "viral_pressure", "unrealistic_promise", "cash_for_all", "alarmist_claim"}) / 0.3 * 100),
                   scheme_risk],
    }
    breakdown["values"] = [min(v, 100) for v in breakdown["values"]]

    explanation = _explain(verdict, label, flags, urls, scheme, ml_p, ml_terms, has_official)
    safe_note = _actions(verdict)

    return {
        "verdict": verdict, "label": label, "risk": round(risk * 100),
        "ml_probability": None if ml_p is None else round(ml_p * 100, 1),
        "rule_score": round(rule_score * 100),
        "flags": [f.to_dict() for f in flags],
        "urls": urls,
        "scheme": _scheme_view(scheme),
        "explanation": explanation, "safe_actions": safe_note,
        "ml_terms": ml_terms, "breakdown": breakdown, "engine": engine,
        "input_type": input_type,
    }


def _scheme_view(s):
    if s["status"] == "verified_match":
        sc = s["scheme"]
        return {"status": "verified_match", "name": sc["name"], "ministry": sc["ministry"], "benefit": sc["benefit"],
                "official_url": sc["official_url"], "note": "Official registration/information for this scheme does not require paying agents or private links."}
    if s["status"] == "claimed_not_found":
        return {"status": "claimed_not_found", "claimed": s["claimed"]}
    return {"status": "no_scheme_claim"}


def _explain(verdict, label, flags, urls, scheme, ml_p, ml_terms, has_official):
    parts = []
    if verdict == "fake":
        parts.append("InfoShield rates this message as high risk.")
    elif verdict == "verify":
        parts.append("The signals are mixed, so InfoShield cannot confirm this message either way. Treat it as unverified.")
    else:
        parts.append("InfoShield found no strong scam signals in this message.")
    if flags:
        parts.append("Main reasons: " + "; ".join(f.title.lower() for f in sorted(flags, key=lambda f: -f.weight)[:4]) + ".")
    if has_official and verdict == "genuine":
        parts.append("The link points to an official .gov.in / .nic.in domain.")
    if scheme["status"] == "verified_match" and verdict != "fake":
        parts.append(f"The scheme matches '{scheme['scheme']['name']}' in the verified list.")
    if ml_p is not None:
        s = f"The text classifier scored it {ml_p*100:.0f}% likely to be a scam"
        if ml_terms and ml_p >= 0.5:
            s += " (influential words: " + ", ".join(ml_terms[:4]) + ")"
        parts.append(s + ".")
    parts.append("This is a decision-support tool, not an official ruling. Confirm on myscheme.gov.in or PIB Fact Check.")
    return " ".join(parts)


def _actions(verdict):
    if verdict == "fake":
        return ["Do not click the link or pay anything.", "Never share OTP, PIN, Aadhaar or bank details.",
                "Report at cybercrime.gov.in or call 1930 if you already lost money.", "Warn your family and groups, but do not forward the original message."]
    if verdict == "verify":
        return ["Search the scheme name on myscheme.gov.in.", "Check pib.gov.in/factcheck before forwarding.",
                "Do not pay or share personal details until it is verified."]
    return ["Still use only the official portal for applications.", "Government schemes do not charge agents to register."]
