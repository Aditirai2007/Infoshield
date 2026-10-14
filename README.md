# InfoShield - AI-Powered Detection of Fake Government Schemes and Misinformation

Mini Project ID 2026-27CSEMPID003 | ABES Institute of Technology, Ghaziabad

A working prototype: web frontend + FastAPI backend + trained text classifier + scam-rule engine + link checker + verified-scheme database + screenshot OCR + SQLite community log.

## 1. Setup (one time)

```bash
cd infoshield/backend
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r ../requirements.txt
python train_model.py          # trains the model with YOUR scikit-learn version, saves metrics
python test_demo_cases.py      # sanity check on 24 messages that are not in the dataset
```

`data/dataset.csv` is already included. `python data/build_dataset.py` regenerates it.

**Screenshot OCR** needs the Tesseract program installed separately:
- Windows: install the UB Mannheim build of Tesseract, then set `TESSERACT_CMD` to the path of `tesseract.exe` (for example `set TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe`).
- Ubuntu: `sudo apt install tesseract-ocr tesseract-ocr-hin`
- If Tesseract is missing, only the Screenshot tab shows an error. Everything else still works.

## 2. Run

```bash
cd infoshield/backend
uvicorn main:app --reload
```

Open **http://localhost:8000**. The website is served by the same server. API docs are at http://localhost:8000/docs.

The page needs internet for the Tailwind, Chart.js and Font Awesome files it loads from CDNs. For a demo without internet, open the page once online first, or download those files and link them locally.

## 3. How it works

```
Input (text / link / screenshot)
  -> OCR                Tesseract (screenshots only)
  -> url_checker.py     .gov.in/.nic.in? risky extension, shortener, look-alike name, .apk, raw IP
  -> rules.py           fee demand, OTP/PIN ask, urgency, too-good promise, forward-to-N,
                        cash-for-all, alarmist claim (English + Hindi + Hinglish; negation-aware,
                        so "never share your OTP" is not flagged)
  -> scheme_matcher.py  22 verified schemes in data/schemes.json; spots "real name, unsafe details"
  -> train_model.py     TF-IDF (word + character n-grams) + Logistic Regression -> scam probability
  -> analyzer.py        risk = 0.5 x classifier + 0.5 x rules, plus safety overrides
                        65% and above: Likely Fake | 35-65%: Needs Verification | below 35%: Likely Genuine
  -> JSON: verdict, risk, flags, explanation, per-component chart data, scheme card, safe actions
```

| File | Role |
|---|---|
| `backend/main.py` | FastAPI endpoints: `/api/analyze`, `/analyze-url`, `/analyze-image`, `/report`, `/reports`, `/reports/export`, `/stats`, `/schemes`, `/model-info`, `/health` |
| `backend/analyzer.py` | Pipeline that combines all checks (testable without the web server) |
| `backend/rules.py`, `url_checker.py`, `scheme_matcher.py` | Explainable detection logic |
| `backend/train_model.py` | Training, comparison of 3 models, metrics, confusion matrix |
| `backend/database.py` | SQLite: scans and community reports (created on first run) |
| `backend/data/` | `schemes.json`, `build_dataset.py`, `dataset.csv` |
| `backend/models/` | `model.pkl`, `metrics.json`, `confusion_matrix.png` |
| `frontend/index.html` | The user interface |

## 4. Honest notes for your report and viva

1. **The dataset is small and synthetic.** It has 321 messages: hand-written ones plus template-generated variants. The train/test split is group-aware (all variants of one template stay on the same side), but the metrics (about 99% accuracy) still describe this dataset, not real WhatsApp traffic. Say this clearly. The 24 cases in `test_demo_cases.py` were written in a similar style, so they are a sanity check, not independent proof.
2. **Make the result stronger** by adding real messages (PIB Fact Check posts, news fact-checks, forwards you receive), re-running `train_model.py`, and reporting the new numbers.
3. **The scheme list has 22 entries.** "Not in the verified list" is shown as a warning, not as proof of fraud. Check each official URL and benefit description against the live portals before you submit.
4. **The link check never opens the website.** It judges the address only (no WHOIS, no live reputation lookup).
5. **Community log rows marked "sample"** are demo entries. Entries saved from the page are real rows in `infoshield.db`.
6. **Translation:** the language selector translates the headline for six languages, and the headline, description and scan button for Hindi. Detection itself works on English, Hindi and Hinglish text.
7. This is a **decision-support tool**, not an official ruling.

## 5. Suggested 5-minute demo

1. Problem (1 min): fake scheme messages, one real example.
2. Architecture diagram (30 s): the flow above.
3. Live demo (2 min): quick-test **Fake** (red, flags, chart), **Genuine** (green), **Viral forward** (amber). Then the **URL tab** with `pmkisan-gov.in/register`, then a screenshot.
4. Scam Simulator (30 s): set the link ending to `.gov.in` and the fee to "No fee required" and watch the score drop.
5. Model evaluation panel and limitations (1 min).

## 6. Troubleshooting

- *Banner says backend offline*: start `uvicorn` from the `backend` folder.
- *"Model file missing" or a pickle warning*: run `python train_model.py`.
- *Screenshot error*: install Tesseract (see above).
- *Port busy*: `uvicorn main:app --port 8001`, then open `http://localhost:8001`.
