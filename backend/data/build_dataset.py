"""
Builds dataset.csv for InfoShield.

IMPORTANT (be honest in your report): this is a SYNTHETIC / hand-written starter
dataset. It mixes hand-written messages with template-generated variants. Each
template (and each hand-written message) has its own `group` id so that the
train/test split in train_model.py keeps all variants of one template on the
SAME side of the split. That makes the reported metrics less inflated, but the
numbers still describe THIS dataset, not real-world WhatsApp traffic.
To improve the project, add real messages (PIB Fact Check, news, your own forwards).
"""
import csv, random
random.seed(42)

# ---------------- hand-written FAKE / misleading (label = 1) ----------------
FAKE_HAND = [
 ("fee_trap", "Urgent! PM Free Laptop Scheme 2026: All college students are eligible to receive a free HP laptop. Click http://pmscheme-laptop.site and pay Rs. 499 processing fee to claim today!"),
 ("fee_trap", "Congratulations! You are selected for PM Awas Yojana subsidy of Rs 2.5 lakh. Deposit Rs 1200 security fee at http://pmay-subsidy.online to release the amount."),
 ("fee_trap", "Ayushman Bharat new card registration open. Pay Rs 299 registration charge on www.ayushman-card-apply.xyz and get your card in 24 hours."),
 ("fee_trap", "Govt scholarship Rs 25000 approved for you. Send Rs 150 verification fee on UPI 98xxxxxx21 to receive the amount."),
 ("fee_trap", "PM Kisan new installment pending. Pay Rs 99 activation fee at kisan-yojana.top to unlock your Rs 4000."),
 ("fee_trap", "Free scooty for all girl students under PM Scooty Yojana. Registration fee Rs 350 only. Apply fast http://scooty-yojana.click"),
 ("fee_trap", "Sarkari naukri yojana: Register today with Rs 500 fees and get guaranteed government job letter. Link: http://sarkari-job-yojana.tech"),
 ("fee_trap", "PM Free Mobile Yojana 2026 - get a free smartphone. Pay Rs 199 delivery charge now: bit.ly/free-mobile-pm"),
 ("fee_trap", "Free solar panel scheme by Government. Book now by paying Rs 999 advance at http://pm-solar-free.live. Limited slots."),
 ("fee_trap", "Mudra loan of 10 lakh approved without documents. Pay Rs 2000 processing fee first. WhatsApp us on +91 9XXXXXXXXX."),
 ("fee_trap", "Apna ration card update karne ke liye abhi Rs 250 fees jama karein is link par: http://ration-update.site. Aaj last date hai."),
 ("fee_trap", "PM Berojgari Bhatta Rs 3500 every month. Register by paying Rs 100 at www.berojgari-bhatta.xyz today only."),
 ("fee_trap", "फ्री लैपटॉप योजना 2026: सभी छात्रों को मुफ्त लैपटॉप। आज ही 499 रुपये फीस जमा करें http://laptop-yojana.site"),
 ("fee_trap", "प्रधानमंत्री आवास योजना में नाम आया है। 1500 रुपये रजिस्ट्रेशन शुल्क तुरंत भेजें और पैसा पाएं।"),
 ("fee_trap", "Gas subsidy of Rs 3000 stuck. Pay Rs 75 clearance fee through the link gas-subsidy-india.top to get it credited."),
 ("phishing", "Dear customer your PM Kisan KYC is expired. Share your Aadhaar number and OTP on this link http://pmkisan-kyc-update.site to avoid account block."),
 ("phishing", "Your Ayushman card will be blocked in 24 hours. Download the apk from http://ayushman-update.xyz/app.apk and enter your bank details and OTP."),
 ("phishing", "Govt of India: Aadhaar linking pending. Send your Aadhaar and PIN to 98XXXXXXX0 within 1 hour or your subsidy will stop."),
 ("phishing", "Your LPG subsidy is on hold. Verify your bank account number and CVV at http://lpg-subsidy-verify.click to receive Rs 4000."),
 ("phishing", "Income tax refund approved under new government yojana. Login with netbanking password at http://incometax-refund-gov.online now."),
 ("phishing", "Important notice: Your PAN will be cancelled. Update immediately and enter OTP received at http://pan-update-india.tech"),
 ("phishing", "PM Awas beneficiary list released. Download the app http://pmay-list.top/pm.apk and login with your Aadhaar OTP to check your name."),
 ("phishing", "आपका जन धन खाता बंद हो जाएगा। तुरंत अपना ओटीपी और आधार नंबर इस लिंक पर भेजें: http://jandhan-kyc.site"),
 ("phishing", "Scholarship KYC verification needed. Enter your debit card number, expiry and PIN at www.scholarship-kyc.xyz else payment will be cancelled."),
 ("phishing", "Ration card holders: confirm your Aadhaar and OTP on http://ration-verify.site by tonight or card is deactivated."),
 ("cash_grant", "Government is giving Rs 2000 cash grant to everyone due to upcoming festival season. Share this message to 10 friends to claim bonus."),
 ("cash_grant", "Modi ji ne announce kiya hai har student ko Rs 5000 free. Apply at http://modi-student-grant.site and forward to 5 groups."),
 ("cash_grant", "Breaking: PM giving free Rs 10,000 to all citizens, double of last year! Click now and get money in 2 minutes. No documents needed."),
 ("cash_grant", "Free recharge of Rs 599 for 3 months to all Indians by Modi government. Click link and share with 20 contacts: http://free-recharge-modi.live"),
 ("cash_grant", "Government has deposited Rs 7500 in everyone's account under new scheme. Check balance on http://check-pm-balance.xyz before it expires tonight."),
 ("cash_grant", "सरकार हर परिवार को 5000 रुपये मुफ्त दे रही है। इस मैसेज को 10 ग्रुप में शेयर करें तभी पैसा मिलेगा।"),
 ("cash_grant", "Student Monthly Cash Grant Rs 2500 for every college student from govt. Guaranteed. Apply at student-grant-india.tech and share to unlock."),
 ("cash_grant", "Unemployed youth will get Rs 6000 per month from tomorrow, announced by PM. Forward this to all your friends and apply on youth-bhatta.click."),
 ("viral_forward", "ALERT: Government will shut down all banks for 10 days from tomorrow. Withdraw all your cash today. Forward to everyone!"),
 ("viral_forward", "Forwarded as received: New rule - from next month all WhatsApp users must pay Rs 500 or account will be deleted by the government. Share with all."),
 ("viral_forward", "Govt has banned all Rs 500 notes from midnight. Send this to your family now before it is too late!!"),
 ("viral_forward", "Breaking news: Every citizen gets free petrol for 1 year from govt. Message is confirmed by officials. Share to 15 groups to avail."),
 ("viral_forward", "NASA confirmed Indian govt cash scheme will triple your savings if you forward this message to 10 people within 1 hour."),
 ("viral_forward", "सरकार ने कल से सभी एटीएम बंद करने का आदेश दिया है, आज ही पैसे निकाल लें। सभी को फॉरवर्ड करें।"),
 ("viral_forward", "Ministry says free ration for 5 years is cancelled and all ration cards will be blocked unless you share this post with 10 people."),
 ("viral_forward", "WARNING: Government to read all your WhatsApp chats from tomorrow. Forward this message to avoid being banned."),
 ("fake_portal", "Official PM Kisan registration portal: www.pmkisan-gov.in Apply today, limited seats, first come first served."),
 ("fake_portal", "Apply for national scholarship 2026 only on www.nsp-scholarship.in/apply - hurry, portal closes tonight at midnight!"),
 ("fake_portal", "Check Aadhaar update status and claim your Rs 3000 incentive at http://uidai-gov.in.help/claim"),
 ("fake_portal", "Government of India Yojana portal gov-india-yojana.com: register now for guaranteed benefits, last date today!"),
 ("fake_portal", "Download e-Shram card and get Rs 3000 per month at https://eshram-gov.online/register. Limited time offer."),
 ("fake_portal", "Free ration card online apply at ration-card-online.xyz. Instant approval, pay small processing charges."),
 ("job_loan", "Railway recruitment 2026: 5000 posts, direct joining without exam. Pay Rs 1500 training fee to book your seat at railway-jobs-india.site."),
 ("job_loan", "PM Rozgar Yojana: guaranteed government job for 12th pass youth. Send Rs 800 registration to confirm your appointment letter."),
 ("job_loan", "Urgent hiring by Central Govt, salary Rs 40000, no interview. Click http://central-job.top and pay Rs 600 form fee."),
 ("job_loan", "Pradhan Mantri instant loan up to Rs 5 lakh in 10 minutes without CIBIL check. Pay Rs 999 insurance first via bit.ly/pm-instant-loan."),
 ("fee_trap", "PM Vishwakarma toolkit free delivery at your home. Pay Rs 120 courier charge at pmvishwakarma-toolkit.site to confirm."),
 ("fee_trap", "Beti Bachao Yojana: Rs 50000 for every girl child. Pay Rs 199 registration on beti-yojana-apply.xyz, offer ends tonight."),
 ("phishing", "Your electricity subsidy KYC is pending. Update now with Aadhaar, PAN and OTP at http://bijli-subsidy-kyc.top or connection will be cut tonight."),
 ("phishing", "e-Shram card suspended! Re-verify instantly by sharing your bank account number and ATM PIN with our officer on +91 8XXXXXXXXX."),
 ("cash_grant", "Free laptop, free scooty and Rs 5000 cash for all students under PM Yojana. Click and apply at once: http://pm-student-yojana.site"),
 ("viral_forward", "Government will give Rs 1000 to everyone who forwards this to 20 contacts. Official announcement. Do not ignore."),
 ("fee_trap", "Aapke naam par Rs 50000 ki sarkari yojana nikli hai. Paisa lene ke liye Rs 500 pehle jama karein. Offer sirf aaj ke liye."),
 ("cash_grant", "PM Mahila Samman: every woman gets Rs 7000 per month from this Sunday. Register at mahila-samman-yojana.click and share on 10 groups."),
]

# ---------------- hand-written GENUINE (label = 0) ----------------
GENUINE_HAND = [
 ("official_info", "Under PM Awas Yojana (PMAY-U), eligible urban beneficiaries can apply directly through the official portal. Visit https://pmaymis.gov.in for criteria. No fee required."),
 ("official_info", "PM-KISAN provides income support to eligible farmer families. Check your beneficiary status on https://pmkisan.gov.in. Registration is free of cost."),
 ("official_info", "You can check eligibility for central and state schemes on https://www.myscheme.gov.in. The portal is free to use and does not ask for any payment."),
 ("official_info", "Students can apply for scholarships on the National Scholarship Portal https://scholarships.gov.in. Keep your Aadhaar, income certificate and marksheet ready. There is no application fee."),
 ("official_info", "Ayushman Bharat PM-JAY covers hospitalisation costs for eligible families. Check eligibility at https://pmjay.gov.in or call the official helpline."),
 ("official_info", "e-Shram registration for unorganised workers is free. Register at https://eshram.gov.in or visit the nearest Common Service Centre."),
 ("official_info", "PM Ujjwala Yojana offers LPG connections to eligible women. Applications can be made through your LPG distributor or at https://pmuy.gov.in."),
 ("official_info", "Aadhaar address update can be done online at https://uidai.gov.in using your registered mobile number. The portal never asks you to pay outside the listed fee."),
 ("official_info", "DigiLocker is a free government service to store documents digitally. Access it at https://www.digilocker.gov.in."),
 ("official_info", "The PM Vishwakarma scheme supports traditional artisans. Registration is done through the official portal https://pmvishwakarma.gov.in or Common Service Centres."),
 ("official_info", "Jan Dhan accounts can be opened at any bank branch with basic KYC documents. Details are available at https://pmjdy.gov.in."),
 ("official_info", "Apply for MGNREGA job card at your Gram Panchayat. Information on the programme is available on https://nrega.nic.in. Job cards are issued free of charge."),
 ("official_info", "PM SVANidhi offers working capital loans to street vendors. Details and application are available at https://pmsvanidhi.mohua.gov.in."),
 ("official_info", "ABHA (health ID) creation is voluntary and free of cost. Learn more at https://abdm.gov.in."),
 ("official_info", "PM Surya Ghar Muft Bijli Yojana provides subsidy for rooftop solar. Apply only through the national portal https://pmsuryaghar.gov.in."),
 ("official_info", "प्रधानमंत्री किसान सम्मान निधि का स्टेटस आप https://pmkisan.gov.in पर देख सकते हैं। इसके लिए कोई शुल्क नहीं है।"),
 ("official_info", "आयुष्मान भारत योजना के लिए पात्रता जांचने हेतु https://pmjay.gov.in पर जाएं। आवेदन पूरी तरह निःशुल्क है।"),
 ("official_info", "PM Kisan ki agli kisht ki jaankari ke liye official site https://pmkisan.gov.in dekhein. Koi fees nahi lagti."),
 ("official_info", "Ration card se jude sawalon ke liye apne state ke food department ya https://nfsa.gov.in par jaayein. Seva nishulk hai."),
 ("advisory", "PIB Fact Check: A message claiming free laptops for all students under a PM scheme is fake. The government has not announced any such scheme."),
 ("advisory", "Beware of fraud calls. Government departments never ask for your OTP, PIN or bank password. Do not share these with anyone."),
 ("advisory", "Never share your OTP with anyone, even if they claim to be from a government office or bank. Report suspicious messages at cybercrime.gov.in."),
 ("advisory", "Cyber safety tip: Genuine government websites end with .gov.in or .nic.in. Do not pay any registration fee to claim a scheme benefit through private links."),
 ("advisory", "Fact check: The viral message claiming all banks will be closed for 10 days is false. Do not forward it."),
 ("advisory", "If you receive a call asking for your Aadhaar OTP for scheme benefits, do not share it. Report the number at the national cyber crime portal."),
 ("advisory", "Government schemes do not charge any fee for registration. If someone asks for money, it is a scam. Report it at cybercrime.gov.in or call 1930."),
 ("advisory", "सावधान रहें: कोई भी सरकारी विभाग आपसे ओटीपी या पिन नहीं मांगता। किसी के साथ अपना ओटीपी साझा न करें।"),
 ("advisory", "PIB Fact Check has clarified that the viral post about Rs 5000 cash for every citizen is fake. Please do not share unverified messages."),
 ("advisory", "Reminder: official scheme applications never require payment to private UPI IDs. Verify on myscheme.gov.in before you act."),
 ("news", "The Ministry released the revised guidelines for the scholarship scheme today. Students are advised to read the notification published on the official website."),
 ("news", "The Cabinet approved an extension of the rooftop solar subsidy programme. Households can find the application steps on the official national portal."),
 ("news", "Government launches a new digital health initiative to help citizens store medical records securely with consent, the Health Ministry said in a statement."),
 ("news", "The Reserve Bank said there is no plan to withdraw any currency note from circulation, and appealed to the public to ignore false rumours."),
 ("news", "Ministry of Education announced the schedule for the national scholarship application window. Applicants should complete verification through their institution."),
 ("news", "The labour ministry said registration on the e-Shram portal crossed a major milestone. Workers can register free of cost at the portal."),
 ("news", "State government announced the release of the next instalment of the farmer income support scheme through direct benefit transfer to bank accounts."),
 ("how_to", "To check your PM-KISAN status: open pmkisan.gov.in, click Know Your Status, enter your registration number and captcha. The service is free."),
 ("how_to", "To download e-Aadhaar, go to uidai.gov.in, choose Download Aadhaar, enter your Aadhaar number and the OTP sent to your registered mobile. Keep your OTP private."),
 ("how_to", "To find a scheme for you: visit myscheme.gov.in, answer a few questions about yourself, and the portal will list the schemes you may be eligible for."),
 ("how_to", "Create a free DigiLocker account at digilocker.gov.in using your mobile number. You can then fetch documents like driving licence and marksheets."),
 ("how_to", "Scholarship applicants: register on scholarships.gov.in, fill the application form, upload documents, and submit before the last date mentioned on the portal."),
 ("how_to", "Visit your nearest Common Service Centre for help with online scheme applications. Ask for the official receipt and do not pay more than the notified service charge."),
 ("how_to", "आयुष्मान कार्ड बनवाने के लिए नजदीकी आयुष्मान मित्र या कॉमन सर्विस सेंटर से संपर्क करें। अधिक जानकारी pmjay.gov.in पर उपलब्ध है।"),
 ("how_to", "ई-श्रम कार्ड के लिए eshram.gov.in पर अपना मोबाइल नंबर और आधार से रजिस्ट्रेशन करें। यह सेवा मुफ्त है।"),
 ("official_info", "The National Food Security Act provides subsidised foodgrains to eligible households through ration cards. Check details on https://nfsa.gov.in."),
 ("official_info", "Sukanya Samriddhi accounts can be opened at post offices and authorised banks. Visit https://www.indiapost.gov.in for details."),
 ("official_info", "Atal Pension Yojana is available through your bank. Details at https://jansuraksha.gov.in. Contact your bank branch for enrolment."),
 ("news", "Officials said farmers should only use the official portal for scheme updates and avoid links received on social media."),
 ("advisory", "Be careful with apk files shared on WhatsApp in the name of government schemes. Install apps only from the official Play Store listing of the department."),
 ("advisory", "Scam alert: Fraudsters are sending fake links in the name of Ayushman Bharat. Genuine information is only on pmjay.gov.in. No one should ask you for money."),
 ("how_to", "Swachh Bharat toilet incentive applications are handled through your Gram Panchayat or urban local body. See https://swachhbharatmission.gov.in for guidelines."),
 ("news", "The Finance Ministry clarified that no new fee has been introduced for Jan Dhan accounts and urged citizens not to believe fake forwards."),
 ("official_info", "Beti Bachao Beti Padhao is an awareness and welfare campaign run through district administrations. See https://wcd.nic.in for official updates."),
 ("how_to", "For Aadhaar-related help, call the UIDAI toll free helpline 1947 or visit https://uidai.gov.in. Never share your OTP or biometric details with strangers."),
 ("news", "The department has issued a public notice that scheme benefits are transferred directly to bank accounts and no middleman is authorised to collect any money."),
 ("official_info", "Mudra loans are offered by banks and financial institutions for small businesses. Visit your nearest bank branch or check the details on myscheme.gov.in."),
 ("how_to", "Street vendors can apply for PM SVANidhi through the official portal or the Urban Local Body. There is no registration fee."),
 ("advisory", "PIB Fact Check: Claims that all ration cards will be cancelled unless a message is forwarded are fake. Government has not issued such an order."),
]

# ---------------- templates (each template = one group) ----------------
FAKE_SCHEMES = ["PM Free Laptop Yojana", "PM Student Cash Grant", "Free Scooty Yojana", "PM Free Mobile Yojana",
                "Modi Free Recharge Scheme", "PM Berojgari Bhatta", "Free Solar Panel Yojana", "Free Gas Cylinder Offer",
                "PM Mahila Samman Yojana", "Free Tablet Yojana", "PM Kisan Bonus Yojana", "Free Smartphone Yojana 2026"]
FAKE_WORDS = ["pm", "yojana", "sarkari", "gov", "india", "scheme", "modi", "kisan", "student", "free"]
FAKE_TLDS = [".site", ".xyz", ".top", ".click", ".online", ".live", ".tech", ".icu", ".buzz", ".shop"]
FEES = ["99", "149", "199", "299", "350", "499", "750", "999", "1200", "1500"]
URGENCY = ["Urgent!", "Last date is today!", "Offer expires at midnight!", "Apply now before seats fill!", "Hurry, only 100 slots left!", "Limited time only!"]
REAL_NAMES = ["PM-KISAN", "PM Awas Yojana", "Ayushman Bharat", "PM Ujjwala Yojana", "National Scholarship Portal", "e-Shram", "Jan Dhan Yojana", "DigiLocker", "myScheme", "PM Vishwakarma"]
REAL_DOMAINS = ["pmkisan.gov.in", "pmaymis.gov.in", "pmjay.gov.in", "pmuy.gov.in", "scholarships.gov.in", "eshram.gov.in", "pmjdy.gov.in", "digilocker.gov.in", "myscheme.gov.in", "pmvishwakarma.gov.in"]

def fdomain():
    a, b = random.sample(FAKE_WORDS, 2)
    return f"{a}-{b}{random.choice(FAKE_TLDS)}"

FAKE_TEMPLATES = [
 ("fee_trap", lambda: f"{random.choice(URGENCY)} {random.choice(FAKE_SCHEMES)}: pay Rs {random.choice(FEES)} registration fee at http://{fdomain()} to claim your benefit."),
 ("fee_trap", lambda: f"Congratulations, you have been selected for {random.choice(FAKE_SCHEMES)}. Deposit Rs {random.choice(FEES)} processing charge on www.{fdomain()} within 2 hours."),
 ("fee_trap", lambda: f"{random.choice(FAKE_SCHEMES)} approved in your name. Send Rs {random.choice(FEES)} on UPI to confirm. {random.choice(URGENCY)}"),
 ("phishing", lambda: f"Your {random.choice(['PM Kisan','Ayushman','Jan Dhan','ration card','scholarship'])} KYC has expired. Send your Aadhaar number and OTP at http://{fdomain()} or the account will be blocked."),
 ("phishing", lambda: f"{random.choice(URGENCY)} Verify your bank details and PIN for {random.choice(FAKE_SCHEMES)} at {fdomain()} else benefit will be cancelled."),
 ("cash_grant", lambda: f"Government is giving Rs {random.choice(['1000','2000','3000','5000','7500','10000'])} to every citizen under {random.choice(FAKE_SCHEMES)}. Share this with {random.choice(['5','10','15','20'])} friends to receive the money."),
 ("cash_grant", lambda: f"Breaking: {random.choice(FAKE_SCHEMES)} announced by PM! Free money for all. Click http://{fdomain()} and forward to {random.choice(['5','10','20'])} groups. {random.choice(URGENCY)}"),
 ("viral_forward", lambda: f"ALERT from government: {random.choice(['banks will be closed for a week','all ATMs will shut from tomorrow','Rs 500 notes will be banned tonight','WhatsApp will start charging users from next month'])}. Forward this to everyone you know immediately!"),
 ("fake_portal", lambda: f"Official registration for {random.choice(FAKE_SCHEMES)} now open at www.{random.choice(['pmkisan','pmay','ayushman','eshram','scholarship'])}-{random.choice(['gov','govt','sarkar','india'])}{random.choice(FAKE_TLDS)}. {random.choice(URGENCY)}"),
 ("fee_trap", lambda: f"{random.choice(FAKE_SCHEMES)}: delivery charge Rs {random.choice(FEES)} only, rest is free from government. Book at bit.ly/{random.choice(['pm-free','yojana-now','sarkari-offer'])}{random.randint(1,99)}"),
]
GENUINE_TEMPLATES = [
 ("official_info", lambda: (lambda i: f"{REAL_NAMES[i]} information and application details are available on the official portal https://{REAL_DOMAINS[i]}. The service is free of cost.")(random.randrange(len(REAL_NAMES)))),
 ("official_info", lambda: (lambda i: f"To know your eligibility for {REAL_NAMES[i]}, visit https://{REAL_DOMAINS[i]}. No registration fee is charged by the government.")(random.randrange(len(REAL_NAMES)))),
 ("advisory", lambda: (lambda i: f"Scam alert: do not pay any money to claim {REAL_NAMES[i]} benefits through private links. Official information is only at {REAL_DOMAINS[i]}.")(random.randrange(len(REAL_NAMES)))),
 ("how_to", lambda: (lambda i: f"How to apply for {REAL_NAMES[i]}: open {REAL_DOMAINS[i]}, register with your mobile number, fill in the form and upload documents. Never share your OTP with anyone.")(random.randrange(len(REAL_NAMES)))),
 ("news", lambda: (lambda i: f"The ministry said updates on {REAL_NAMES[i]} will be published on the official website and citizens should ignore unverified messages on social media.")(random.randrange(len(REAL_NAMES)))),
 ("advisory", lambda: f"PIB Fact Check: The viral message about {random.choice(['free laptops','Rs 5000 cash for all','bank closure for 10 days','free recharge'])} is fake. The government has not announced anything like this. Do not forward it."),
 ("official_info", lambda: (lambda i: f"आप {REAL_NAMES[i]} की जानकारी आधिकारिक पोर्टल https://{REAL_DOMAINS[i]} पर देख सकते हैं। कोई शुल्क नहीं लगता।")(random.randrange(len(REAL_NAMES)))),
 ("how_to", lambda: (lambda i: f"Visit the nearest Common Service Centre for help with {REAL_NAMES[i]}. Ask for an official receipt. More details at {REAL_DOMAINS[i]}.")(random.randrange(len(REAL_NAMES)))),
]

def build():
    rows = []
    for i, (cat, t) in enumerate(FAKE_HAND):
        rows.append((t, 1, cat, f"hand_f_{i}"))
    for i, (cat, t) in enumerate(GENUINE_HAND):
        rows.append((t, 0, cat, f"hand_g_{i}"))
    seen = {r[0] for r in rows}
    for k, (cat, fn) in enumerate(FAKE_TEMPLATES):
        n, tries = 0, 0
        while n < 14 and tries < 400:
            tries += 1
            t = fn()
            if t not in seen:
                seen.add(t); rows.append((t, 1, cat, f"tpl_f_{k}")); n += 1
    for k, (cat, fn) in enumerate(GENUINE_TEMPLATES):
        n, tries = 0, 0
        while n < 16 and tries < 400:
            tries += 1
            t = fn()
            if t not in seen:
                seen.add(t); rows.append((t, 0, cat, f"tpl_g_{k}")); n += 1
    random.shuffle(rows)
    with open("dataset.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["text", "label", "category", "group"])
        w.writerows(rows)
    fake = sum(1 for r in rows if r[1] == 1)
    print(f"dataset.csv written: {len(rows)} rows ({fake} fake/misleading, {len(rows)-fake} genuine)")

if __name__ == "__main__":
    build()
