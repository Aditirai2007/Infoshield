"""Screenshot OCR using Tesseract (install the Tesseract engine separately)."""
import io, os
from PIL import Image, ImageOps

try:
    import pytesseract
except Exception:  # pragma: no cover
    pytesseract = None
else:
    if os.environ.get("TESSERACT_CMD"):  # Windows: set TESSERACT_CMD to the full path of tesseract.exe
        pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]


def _lang():
    try:
        langs = set(pytesseract.get_languages(config=""))
    except Exception:
        return "eng"
    wanted = [l for l in ("eng", "hin") if l in langs]
    return "+".join(wanted) or "eng"


def image_to_text(data: bytes) -> str:
    if pytesseract is None:
        raise RuntimeError("pytesseract is not installed (pip install pytesseract) and Tesseract OCR must be installed on the system.")
    img = Image.open(io.BytesIO(data))
    img = ImageOps.exif_transpose(img).convert("L")
    if img.width < 1000:  # upscale small screenshots for better accuracy
        f = 1000 / img.width
        img = img.resize((int(img.width * f), int(img.height * f)))
    img = ImageOps.autocontrast(img)
    try:
        text = pytesseract.image_to_string(img, lang=_lang())
    except pytesseract.TesseractNotFoundError:
        raise RuntimeError("Tesseract OCR engine not found. Install it (see README) and restart the server.")
    return " ".join(text.split())
