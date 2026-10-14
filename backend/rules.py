"""Rule engine: explainable scam red-flag detection (English, Hindi, Hinglish)."""
import re
from dataclasses import dataclass, asdict

NEGATORS = r"(?:no|not|never|without|don'?t|do not|dont|nahi|nahin|kabhi nahi|मत|नहीं|कोई)"


@dataclass
class Flag:
    id: str
    title: str
    detail: str
    level: str      # high / medium / low
    weight: float   # contribution to rule score (0..1)

    def to_dict(self):
        return asdict(self)


def _negated_before(text: str, start: int, window: int = 35) -> bool:
    seg = text[max(0, start - window):start].lower()
    return re.search(rf"\b{NEGATORS}\b|{NEGATORS}", seg) is not None and re.search(NEGATORS, seg) is not None


def _negated_after(text: str, end: int, window: int = 30) -> bool:
    seg = text[end:end + window].lower()
    return re.search(r"(not required|not charged|not needed|nahi|nahin|नहीं|free of cost|is free|are free|मुफ्त|निःशुल्क|nishulk)", seg) is not None


# ---------- patterns ----------
FEE_WORDS = r"(?:registration|processing|security|verification|activation|delivery|courier|clearance|insurance|training|form|booking|advance|handling)?\s*(?:fee|fees|charge|charges|deposit|shulk|शुल्क|फीस)"
FEE_PAY = re.compile(
    rf"(?i)\b(?:pay|deposit|send|transfer|submit|jama\s*karein|jama\s*kare|bhejein|bhej)\b[^.\n]{{0,40}}?(?:rs\.?|₹|inr|rupees?|रुपये|रुपए)\s*\.?\s*\d[\d,]*"
    rf"|(?:rs\.?|₹|inr)\s*\.?\s*\d[\d,]*\s*(?:only\s*)?(?:as\s*)?{FEE_WORDS}"
    rf"|{FEE_WORDS}\s*(?:of\s*)?(?:rs\.?|₹)\s*\d[\d,]*"
    rf"|\d[\d,]*\s*(?:रुपये|रुपए)\s*(?:की\s*)?(?:फीस|शुल्क|रजिस्ट्रेशन)[^.\n]{{0,25}}?(?:जमा|भेज)"
    rf"|(?:फीस|शुल्क)[^.\n]{{0,25}}(?:जमा|भेज)"
    rf"|(?:जमा|भेज)[^.\n]{{0,25}}(?:फीस|शुल्क)"
    rf"|\b(?:pay|deposit)\s+(?:a\s+)?(?:small\s+)?(?:{FEE_WORDS})"
    rf"|(?:rs\.?|₹)\s*\.?\s*\d[\d,]*\s*(?:ka\s+|ki\s+)?(?:\w+\s+){{0,2}}(?:jama|bhej|bhejein|jama\s*karein|jama\s*kare)\b"
    rf"|\bpay\b[^.\n]{{0,30}}\b(?:upi|fee|charges?)\b"
    rf"|upi[^.\n]{{0,15}}(?:send|pay)|(?:send|pay)[^.\n]{{0,30}}\bupi\b"
)
SENSITIVE_ASK = re.compile(
    r"(?i)\b(?:share|send|enter|provide|give|submit|tell|verify|update|confirm|bhejein|bhej|batayein|dalein|login\s+with)\b"
    r"[^.\n]{0,45}?\b(?:otp|pin|cvv|password|passcode|aadhaar|aadhar|pan\b|bank\s*(?:account|details)|account\s*number|card\s*number|debit\s*card|atm|netbanking|upi\s*pin)"
    r"|(?:ओटीपी|आधार|पिन)[^.\n]{0,30}(?:भेज|शेयर|बताएं|दें)"
    r"|(?:भेज|शेयर|बताएं)[^.\n]{0,30}(?:ओटीपी|आधार|पिन)"
    r"|\benter\b[^.\n]{0,30}\botp\b"
)
URGENCY = re.compile(
    r"(?i)\b(?:urgent|urgently|hurry|immediately|instantly|right now|asap|expires?|expiry|last date (?:is )?today|"
    r"today only|tonight|midnight|within \d+\s*(?:hours?|hrs?|minutes?|mins?)|limited (?:time|slots?|seats?)|"
    r"only \d+\s*(?:slots?|seats?) left|first come|jaldi|abhi|aaj hi|aaj last|sirf aaj|before it is too late|will be blocked|will be cancelled|will be deactivated)\b"
    r"|तुरंत|आज ही|अंतिम तारीख|जल्दी|बंद हो जाएगा|ब्लॉक"
)
PROMISE = re.compile(
    r"(?i)\b(?:free\s+(?:laptop|mobile|smartphone|phone|scooty|tablet|iphone|petrol|recharge|gas|cylinder|solar)|"
    r"(?:laptop|mobile|smartphone|scooty|tablet|recharge)\s+free|"
    r"guaranteed\s+(?:job|benefit|loan|money|approval)|without\s+(?:any\s+)?(?:documents?|interview|exam|cibil)|no\s+documents?\s+needed|"
    r"instant\s+(?:approval|loan)|double\s+(?:your\s+)?money|triple\s+your|direct\s+joining|congratulations[^.]{0,40}selected|you\s+(?:have\s+been|are)\s+selected|selected\s+for)\b"
    r"|फ्री\s*लैपटॉप|मुफ्त\s*लैपटॉप|मुफ्त\s*मोबाइल"
)
VIRAL = re.compile(
    r"(?i)\b(?:forward|share)\b[^.\n]{0,40}?(?:to|with|on|in)?\s*\d+\s*(?:friends?|contacts?|groups?|people|persons?|members?)"
    r"|\b(?:forward|share)\s+(?:this|it)\s+(?:message|post|to everyone|with everyone|to all)\b"
    r"|\bforward(?:ed)?\s+(?:this\s+)?to\s+(?:everyone|all)\b|\bsend\s+this\s+to\s+(?:everyone|your family|all)\b|\bforwarded as received\b"
    r"|\bshare\s+(?:this\s+)?(?:message\s+)?to\s+(?:unlock|claim|avail|receive)\b|\bshare\s+to\s+(?:unlock|claim)\b"
    r"|(?:10|\d+)\s*(?:ग्रुप|दोस्तों|लोगों)[^.\n]{0,15}(?:शेयर|फॉरवर्ड)|(?:शेयर|फॉरवर्ड)\s*करें|सभी को फॉरवर्ड"
)
CASH_CLAIM = re.compile(
    r"(?i)\b(?:govt|government|sarkar|pm|modi(?:\s*ji)?|ministry)\b[^.\n]{0,60}?\b(?:giving|gives|will give|has deposited|deposited|announced|dene|de rahi|de rahe)\b[^.\n]{0,50}?(?:rs\.?|₹)\s*\d"
    r"|(?:every(?:one| citizen| student| woman| family)|all citizens|har\s+(?:student|parivar|citizen)|everyone's account)\b[^.\n]{0,40}(?:rs\.?|₹)\s*\d"
    r"|(?:rs\.?|₹)\s*\d[\d,]*\s*(?:cash|free|bonus|grant|per month|every month|monthly)[^.\n]{0,40}(?:everyone|all|every)"
    r"|सरकार[^.\n]{0,40}(?:रुपये|रुपए)[^.\n]{0,30}(?:मुफ्त|दे रही)|हर\s*परिवार"
)
FALSE_CLAIM = re.compile(
    r"(?i)\b(?:banks?|atms?)\b[^.\n]{0,40}\b(?:closed|shut|shutdown|shut down|banned)\b|\b(?:notes?)\b[^.\n]{0,30}\b(?:banned|cancelled|withdrawn)\b"
    r"|\bwill (?:read|monitor) all your (?:chats|messages)\b|\bwhatsapp\b[^.\n]{0,40}\b(?:charge|pay|deleted)\b|एटीएम बंद"
)
SCHEME_CLAIM = re.compile(
    r"(?i)\b(?:(?:pm|pradhan mantri|modi|cm|mukhyamantri|free|sarkari|national)\s+[A-Za-z0-9\- ]{0,35}?(?:yojana|yojna|scheme|bhatta|grant|offer))\b"
)
ADVISORY_CONTEXT = re.compile(
    r"(?i)\b(?:fact\s*check|is fake|are fake|is false|beware|scam alert|fraud alert|cyber ?crime|cybersafety|cyber safety|do not (?:forward|share|pay|click)|never (?:share|pay|click|ask)|ignore false|ignore unverified|report (?:it|suspicious|the number)|"
    r"clarified|clarif(?:y|ies)|no plan to|dont believe|don't believe|not to believe|should ignore|avoid links)\b|सावधान|फर्जी|झूठ"
)


def _first_unnegated(pattern, text, kind):
    for m in pattern.finditer(text):
        if kind in ("fee", "sensitive") and (_negated_before(text, m.start(), 22) or _negated_after(text, m.end())):
            continue
        return m
    return None


def run_rules(text: str, url_results: list) -> list:
    t = text or ""
    flags = []
    advisory = bool(ADVISORY_CONTEXT.search(t))

    m = _first_unnegated(FEE_PAY, t, "fee")
    if m and not advisory:
        flags.append(Flag("fee_demand", "Asks for money / fee",
                          f"The message asks you to pay (\"{m.group(0).strip()[:60]}\"). Genuine schemes do not ask for advance fees through private links.",
                          "high", 0.42))
    m = _first_unnegated(SENSITIVE_ASK, t, "sensitive")
    if m and not advisory:
        flags.append(Flag("sensitive_info", "Asks for OTP / PIN / Aadhaar / bank details",
                          "Government departments never ask you to share OTP, PIN, passwords or card details over message or link.",
                          "high", 0.5))
    m = URGENCY.search(t)
    if m and not advisory:
        flags.append(Flag("urgency", "Artificial urgency",
                          f"Pressure words found (\"{m.group(0).strip()[:40]}\"). Scammers rush people so they do not verify.",
                          "medium", 0.2))
    m = PROMISE.search(t)
    if m and not advisory:
        flags.append(Flag("unrealistic_promise", "Too-good-to-be-true promise",
                          f"Unrealistic benefit promised (\"{m.group(0).strip()[:50]}\"). Free gadgets or guaranteed money/jobs are common bait.",
                          "medium", 0.25))
    m = VIRAL.search(t)
    if m and not advisory:
        flags.append(Flag("viral_pressure", "Asks you to forward / share",
                          "Genuine benefits are never linked to forwarding a message to friends or groups. This is a chain-message tactic.",
                          "medium", 0.28))
    m = CASH_CLAIM.search(t)
    if m and not advisory:
        flags.append(Flag("cash_for_all", "Blanket cash-giveaway claim",
                          "A claim that the government is giving cash to everyone is a classic misinformation / scam pattern and needs an official source.",
                          "medium", 0.28))
    m = FALSE_CLAIM.search(t)
    if m and not advisory:
        flags.append(Flag("alarmist_claim", "Alarmist claim with no source",
                          "Panic claims (banks closing, notes banned, chats monitored) spread as rumours. Check PIB Fact Check before forwarding.",
                          "medium", 0.3))

    # URL based flags
    bad = [u for u in url_results if not u["is_official"]]
    good = [u for u in url_results if u["is_official"]]
    if bad:
        worst = max(bad, key=lambda u: u["severity"])
        lvl = "high" if worst["severity"] >= 0.6 else "medium"
        flags.append(Flag("suspicious_url", "Suspicious link / domain",
                          "; ".join(worst["findings"][:3]) + ".", lvl, round(0.15 + 0.5 * worst["severity"], 2)))
    if good and not bad:
        pass  # positive evidence handled in analyzer

    if advisory and not flags:
        pass
    return flags
