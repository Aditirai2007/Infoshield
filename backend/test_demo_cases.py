"""
Run:  python test_demo_cases.py
Evaluates the FULL pipeline (ML + rules + scheme DB) on messages that are NOT in dataset.csv.
Written fresh and includes tricky cases (advisories that contain scam words, real portals, borderline forwards).
"""
import sys
from analyzer import analyze, ml_probability

# (text, expected) expected in {"fake","genuine","verify_or_fake"}
CASES = [
 ("Urgent! PM Free Laptop Scheme 2026: All college students are eligible to receive a free HP laptop. Click http://pmscheme-laptop.site and pay Rs. 499 processing fee to claim today!", "fake"),
 ("Under PM Awas Yojana (PMAY-U), eligible urban beneficiaries can apply directly through official portal. Visit https://myscheme.gov.in for criteria. No fee required.", "genuine"),
 ("Government is giving Rs 2000 cash grant to everyone due to upcoming festival season. Share this message to 10 friends to claim bonus.", "verify_or_fake"),
 ("Dear user, your Ayushman card is suspended. Click ayushman-help.top and enter your OTP to reactivate within 1 hour.", "fake"),
 ("Free ration for lifetime! Apply on www.garib-kalyan-ration.xyz, deposit Rs 120 for the e-card today.", "fake"),
 ("PM Kisan: Rs 6000 stuck due to KYC. Send Aadhaar number and OTP to this WhatsApp number to release funds.", "fake"),
 ("Scholarship 2026 for all 12th pass students! Fill the form at scholarship-india-apply.click, small fee Rs 99 only. Last date tonight.", "fake"),
 ("Modi government launches free gas stove scheme. Pay Rs 300 shipping at bit.ly/gas-stove-yojana", "fake"),
 ("Alert: All SIM cards will be blocked from tomorrow unless you forward this message to 10 contacts.", "verify_or_fake"),
 ("Your electricity connection will be cut tonight. Call this officer on 9XXXXXXXXX and share the OTP to stop it.", "fake"),
 ("Check your PM-KISAN beneficiary status on https://pmkisan.gov.in. The service is free and no agent is required.", "genuine"),
 ("Apply for the National Scholarship on scholarships.gov.in. Documents needed: Aadhaar, marksheet, income certificate. No fee is charged.", "genuine"),
 ("Do not share your OTP or PIN with anyone claiming to offer scheme benefits. Report frauds at cybercrime.gov.in.", "genuine"),
 ("PIB Fact Check: The claim that free scooties are being given to all girls under a PM scheme is false. Do not pay anyone.", "genuine"),
 ("The Ministry said the e-Shram portal registration is free. Workers should avoid links from unknown senders.", "genuine"),
 ("DigiLocker lets you keep digital copies of documents. Sign up at https://www.digilocker.gov.in using your mobile number.", "genuine"),
 ("RBI clarifies there is no proposal to ban Rs 500 notes. Public is advised not to believe rumours on social media.", "genuine"),
 ("आपका आयुष्मान कार्ड बंद हो जाएगा, तुरंत ओटीपी भेजें http://card-update.site", "fake"),
 ("Sarkari yojana mein naam aaya hai, Rs 700 jama karein aur 50000 paayein. Aaj hi.", "fake"),
 ("Ujjwala Yojana: apply for LPG connection at your nearest distributor or on pmuy.gov.in. Documents: Aadhaar, ration card.", "genuine"),
 ("Free tablet for every student by state govt! Register now at tablet-yojana.live and share with 15 friends to confirm.", "fake"),
 ("Under Atal Pension Yojana you can get a fixed pension after 60. Visit your bank branch or jansuraksha.gov.in for enrolment.", "genuine"),
 ("Winner! You have been selected for PM Lucky Draw Yojana 2026. Claim Rs 1 lakh by paying Rs 500 tax at lucky-pm.site", "fake"),
 ("New Aadhaar update camp in your ward next Sunday organised by the municipal office. Carry original documents; services are free.", "genuine"),
]


def ok(verdict, exp):
    if exp == "fake": return verdict == "fake"
    if exp == "genuine": return verdict == "genuine"
    return verdict in ("verify", "fake")


def main():
    good = 0
    ml_good = 0
    for text, exp in CASES:
        r = analyze(text)
        passed = ok(r["verdict"], exp)
        good += passed
        p, _ = ml_probability(text)
        ml_pred = "fake" if p is not None and p >= 0.5 else "genuine"
        ml_good += (ml_pred == "fake") == (exp in ("fake", "verify_or_fake"))
        print(f"[{'PASS' if passed else 'FAIL'}] risk={r['risk']:>3}% {r['verdict']:<8} (expected {exp:<14}) ml={0 if p is None else round(p*100):>3}%  | {text[:70]}")
        if not passed:
            print("        flags:", [f['id'] for f in r['flags']])
    n = len(CASES)
    print(f"\nFull pipeline: {good}/{n} = {good/n*100:.0f}%   |   ML model alone: {ml_good}/{n} = {ml_good/n*100:.0f}%")
    return 0 if good >= n * 0.85 else 1


if __name__ == "__main__":
    sys.exit(main())
