"""
InfoShield API.  Run from the backend folder:
    uvicorn main:app --reload
Then open http://localhost:8000  (frontend is served by this app)  and http://localhost:8000/docs (API docs).
"""
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

import analyzer, database, ocr, scheme_matcher, url_checker

app = FastAPI(title="InfoShield API", version="2.0",
              description="Detects fake government-scheme messages and misinformation.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.on_event("startup")
def _startup():
    database.init_db()
    analyzer.load_model()


class TextIn(BaseModel):
    text: str = Field(..., max_length=5000)


class UrlIn(BaseModel):
    url: str = Field(..., max_length=2000)


class ReportIn(BaseModel):
    title: str = Field(..., max_length=140)
    region: str = Field("Not specified", max_length=80)
    risk: float = 0
    verdict: str = "fake"


def _finish(result: dict, input_type: str, text: str):
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    database.log_scan(input_type, text, result["verdict"], result["risk"])
    return result


@app.get("/api/health")
def health():
    return {"status": "ok", "model_loaded": analyzer.load_model() is not None}


@app.post("/api/analyze")
def analyze_text(body: TextIn):
    return _finish(analyzer.analyze(body.text, "text"), "text", body.text)


@app.post("/api/analyze-url")
def analyze_link(body: UrlIn):
    url = body.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="Enter a link to check.")
    # run the full pipeline on the link text itself (URL rules + ML + scheme DB)
    result = analyzer.analyze(url, "url")
    return _finish(result, "url", url)


@app.post("/api/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file (PNG or JPG).")
    data = await file.read()
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image is larger than 8 MB.")
    try:
        text = ocr.image_to_text(data)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read this image.")
    if len(text) < 8:
        raise HTTPException(status_code=422, detail="No readable text found in the screenshot. Try a clearer image.")
    result = analyzer.analyze(text, "image")
    result["extracted_text"] = text
    return _finish(result, "image", text)


@app.post("/api/report")
def report(body: ReportIn):
    rid = database.add_report(body.title, body.region, body.risk, body.verdict)
    return {"ok": True, "id": rid}


@app.get("/api/reports")
def reports():
    return database.list_reports(50)


@app.get("/api/reports/export")
def export_reports():
    return Response(content=database.reports_csv(), media_type="text/csv",
                    headers={"Content-Disposition": "attachment; filename=InfoShield_Scam_Report_Log.csv"})


@app.get("/api/stats")
def stats():
    return database.stats()


@app.get("/api/schemes")
def schemes():
    return scheme_matcher.all_schemes()


@app.get("/api/model-info")
def model_info():
    return analyzer.model_info()


# Serve the frontend from the same server (keep this LAST so /api routes win)
FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="frontend")
