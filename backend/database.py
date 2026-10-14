"""SQLite storage for scans and community reports (standard library only)."""
import sqlite3, csv, io
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "infoshield.db"


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS scans(
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, input_type TEXT, snippet TEXT,
            verdict TEXT, risk REAL);
        CREATE TABLE IF NOT EXISTS reports(
            id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, title TEXT, region TEXT,
            risk REAL, verdict TEXT, status TEXT, is_sample INTEGER DEFAULT 0);
        """)
        n = c.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
        if n == 0:  # sample rows so the demo table is not empty (marked as samples)
            now = datetime.now(timezone.utc)
            rows = [
                ("PM Free Laptop Scheme 2026", "Uttar Pradesh (Ghaziabad)", 92, "fake", "Reported - sample entry"),
                ("Student Monthly Cash Grant Rs 2500", "Delhi NCR", 88, "fake", "Reported - sample entry"),
                ("PM Awas Yojana official portal message", "Maharashtra", 8, "genuine", "Checked - sample entry"),
            ]
            c.executemany("INSERT INTO reports(ts,title,region,risk,verdict,status,is_sample) VALUES(?,?,?,?,?,?,1)",
                          [(now.isoformat(), *r) for r in rows])


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log_scan(input_type, text, verdict, risk):
    with conn() as c:
        c.execute("INSERT INTO scans(ts,input_type,snippet,verdict,risk) VALUES(?,?,?,?,?)",
                  (now(), input_type, (text or "")[:200], verdict, risk))


def add_report(title, region, risk, verdict):
    status = "Reported by citizen - under review" if verdict != "genuine" else "Checked - looks genuine"
    with conn() as c:
        cur = c.execute("INSERT INTO reports(ts,title,region,risk,verdict,status,is_sample) VALUES(?,?,?,?,?,?,0)",
                        (now(), title[:140], region[:80] or "Not specified", risk, verdict, status))
        return cur.lastrowid


def list_reports(limit=50):
    with conn() as c:
        return [dict(r) for r in c.execute("SELECT * FROM reports ORDER BY id DESC LIMIT ?", (limit,))]


def reports_csv() -> str:
    rows = list_reports(1000)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Timestamp (UTC)", "Title", "Region", "Risk %", "Verdict", "Status", "Sample entry"])
    for r in rows:
        w.writerow([r["ts"], r["title"], r["region"], r["risk"], r["verdict"], r["status"], "yes" if r["is_sample"] else "no"])
    return buf.getvalue()


def stats():
    with conn() as c:
        total = c.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
        by = {r["verdict"]: r["n"] for r in c.execute("SELECT verdict, COUNT(*) n FROM scans GROUP BY verdict")}
        reps = c.execute("SELECT COUNT(*) FROM reports WHERE is_sample=0").fetchone()[0]
    return {"scans_total": total, "by_verdict": by, "citizen_reports": reps}
