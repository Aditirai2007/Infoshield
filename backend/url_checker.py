"""URL / domain checks. Pure Python, no network calls (works offline)."""
import re
from urllib.parse import urlparse

OFFICIAL_SUFFIXES = (".gov.in", ".nic.in")
RISKY_TLDS = {".site", ".tech", ".xyz", ".top", ".click", ".online", ".live", ".icu", ".buzz", ".shop",
              ".club", ".vip", ".work", ".loan", ".link", ".cc", ".tk", ".ml", ".ga", ".cf", ".gq",
              ".info", ".store", ".fun", ".rest", ".monster", ".cyou"}
SHORTENERS = {"bit.ly", "tinyurl.com", "cutt.ly", "t.co", "goo.gl", "rb.gy", "is.gd", "shorturl.at",
              "ow.ly", "tiny.cc", "t.ly", "bitly.com"}
IMPERSONATION_WORDS = ("gov", "govt", "sarkar", "sarkari", "yojana", "yojna", "scheme", "pm", "modi",
                       "india", "kisan", "ayushman", "aadhaar", "aadhar", "uidai", "pmay", "nsp",
                       "scholarship", "eshram", "ration", "subsidy")

URL_RE = re.compile(r"""(?ix)
    (?:https?://|www\.)[^\s<>"'\)\]]+                      # http(s):// or www.
  | \b[a-z0-9][a-z0-9\-]{0,60}(?:\.[a-z0-9\-]{1,60})*\.(?:gov\.in|nic\.in|site|tech|xyz|top|click|online|live|icu|buzz|shop|club|vip|work|loan|link|cc|tk|ml|ga|cf|gq|info|store|fun|com|in|org|net|co\.in)\b(?:/[^\s<>"'\)\]]*)?
""")


def extract_urls(text: str):
    urls = []
    for m in URL_RE.finditer(text or ""):
        u = m.group(0).rstrip(".,;:!?")
        # skip e-mail-like fragments such as name@x.com
        start = m.start()
        if start > 0 and text[start - 1] == "@":
            continue
        if u not in urls:
            urls.append(u)
    return urls


def _is_official(host: str) -> bool:
    host = host.lower().strip(".")
    return host in ("gov.in", "nic.in") or host.endswith(OFFICIAL_SUFFIXES)


def check_url(url: str) -> dict:
    """Return {url, host, is_official, severity(0..1), findings[list[str]]}."""
    raw = url.strip()
    parsed = urlparse(raw if "://" in raw else "http://" + raw)
    host = (parsed.hostname or "").lower()
    findings, sev = [], 0.0

    if not host:
        return {"url": raw, "host": "", "is_official": False, "severity": 0.3, "findings": ["Could not read the domain name"]}

    official = _is_official(host)
    if official:
        return {"url": raw, "host": host, "is_official": True, "severity": 0.0,
                "findings": [f"Domain {host} ends with an official government suffix (.gov.in / .nic.in)"]}

    sev = 0.45
    findings.append(f"Domain {host} is NOT a .gov.in / .nic.in government domain")

    if "@" in raw.split("//")[-1].split("/")[0]:
        sev += 0.2; findings.append("URL contains '@' which can hide the real destination")
    if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host):
        sev += 0.3; findings.append("Link uses a raw IP address instead of a domain name")
    if host.startswith("xn--") or ".xn--" in host:
        sev += 0.25; findings.append("Domain uses punycode (possible look-alike characters)")

    base = ".".join(host.split(".")[-2:])
    if host in SHORTENERS or base in SHORTENERS:
        sev += 0.3; findings.append("Shortened link hides the real destination")

    tld = "." + host.split(".")[-1]
    if tld in RISKY_TLDS:
        sev += 0.25; findings.append(f"Domain extension {tld} is commonly used in throw-away scam sites")

    hits = [w for w in IMPERSONATION_WORDS if w in host]
    if hits:
        sev += 0.25
        findings.append("Domain imitates official names (" + ", ".join(sorted(set(hits))[:4]) + ") but is not a government site")
    if "gov" in host and not official:
        sev += 0.1; findings.append("Contains 'gov' in the name to look official (look-alike domain)")
    if host.count("-") >= 2:
        sev += 0.1; findings.append("Domain has many hyphens, typical of look-alike sites")
    if parsed.scheme == "http":
        sev += 0.05; findings.append("Link is not secured with HTTPS")
    if raw.lower().endswith(".apk"):
        sev += 0.3; findings.append("Link downloads an .apk app file, which can contain malware")

    return {"url": raw, "host": host, "is_official": False, "severity": round(min(sev, 1.0), 2), "findings": findings}


def check_all(text: str):
    results = [check_url(u) for u in extract_urls(text)]
    return results
