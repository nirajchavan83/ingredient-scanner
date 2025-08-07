from typing import Optional
from fastapi import APIRouter, Query, UploadFile, File, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models.scan import Scan
from schemas.ingredient_schema import AnalyzeRequest, AnalyzeResponse, IngredientResult, ScanRecord
from services.ocr_service import extract_ingredients_from_image
from services.classify_service import classify_ingredients
from services.recommendation_service import generate_recommendation, assess_suitability, get_health_score
from models.user import User
from dependencies import get_current_user, get_current_user_optional

import shutil
import uuid
import os
import json
import unicodedata
import re

router = APIRouter(tags=["Ingredient Scanning"])

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ OCR Only (no auth required)
@router.post("/ocr")
async def ocr_image(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_current_user_optional)  # ✅ safe for Swagger
):
    file_ext = file.filename.split('.')[-1]
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.{file_ext}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ingredients = extract_ingredients_from_image(file_path)
    return {"ingredients": ingredients}

# ✅ Manual Ingredient Analyze (auth required)
@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_ingredients(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    results = classify_ingredients(request.ingredients)
    recommendation, reasons, _ = generate_recommendation(results)
    suitability = assess_suitability(results)
    score = get_health_score(results)

    # Save to DB
    scan = Scan(
        user_id=current_user.id,
        ingredients_text=", ".join(request.ingredients),
        result_json=json.dumps(results),
        recommendation=recommendation,
        health_score=score
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    return AnalyzeResponse(
        ingredients=[IngredientResult(**r) for r in results],
        recommendation=recommendation,
        reasons=reasons,
        health_score=score,
        suitability=suitability
    )

# ✅ Full Scan (OCR + classify) – auth required
@router.post("/full-scan", response_model=AnalyzeResponse)
async def full_scan(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    file_ext = file.filename.split('.')[-1]
    file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}.{file_ext}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    ingredients = extract_ingredients_from_image(file_path)
    results = classify_ingredients(ingredients)
    recommendation, reasons, _ = generate_recommendation(results)
    suitability = assess_suitability(results)
    score = get_health_score(results)

    scan = Scan(
        user_id=current_user.id,
        image_path=file_path,
        ingredients_text=", ".join(ingredients),
        result_json=json.dumps(results),
        recommendation=recommendation,
        health_score=score
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)

    return AnalyzeResponse(
        ingredients=[IngredientResult(**r) for r in results],
        recommendation=recommendation,
        reasons=reasons,
        health_score=score,
        suitability=suitability
    )

# ✅ History – user-specific
@router.get("/history", response_model=list[ScanRecord])
def get_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Scan).filter(Scan.user_id == current_user.id).order_by(Scan.created_at.desc()).all()

# ✅ PDF export – user-specific
def remove_non_latin(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^\x00-\x7F]+", "", text)

@router.get("/pdf/{scan_id}")
def download_pdf(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        return {"error": "Scan not found or unauthorized"}

    ingredients = remove_non_latin(scan.ingredients_text)
    recommendation = remove_non_latin(scan.recommendation or "")
    score = scan.health_score
    result_list = json.loads(scan.result_json)

    result_summary = "\n".join([
        f"{remove_non_latin(r['ingredient'])} - {remove_non_latin(r['health_impact'])}"
        for r in result_list if 'health_impact' in r
    ])

    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, "Ingredient Scan Report", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(200, 10, f"Ingredients:\n{ingredients}")
    pdf.ln(5)
    pdf.multi_cell(200, 10, f"Recommendation: {recommendation}")
    pdf.multi_cell(200, 10, f"Health Score: {score}/10")
    pdf.ln(5)
    pdf.multi_cell(200, 10, f"Health Summary:\n{result_summary}")

    pdf_path = f"static/report_{scan_id}.pdf"
    pdf.output(pdf_path)

    return FileResponse(pdf_path, media_type="application/pdf", filename=f"report_{scan_id}.pdf")

@router.get("/search")
def search_ingredient(
    q: str = Query(..., alias="q"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    INFO_FILE = "data/ingredient_info.json"

    if not os.path.exists(INFO_FILE):
        return {"error": "ingredient_info.json not found"}

    with open(INFO_FILE, 'r') as f:
        info = json.load(f)

    result = info.get(q.lower())
    return {
        "query": q,
        "description": result or "No description found for this ingredient."
    }
