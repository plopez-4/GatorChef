from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app.deps import verify_firebase_token
from app.firebase_admin_init import db
from app.models import PantryItem, ReceiptUploadResponse
from app.services import ocr_service, receipt_parser, normalizer

router = APIRouter(prefix="/upload", tags=["upload"])

_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.post("/receipt", response_model=ReceiptUploadResponse)
async def upload_receipt(
    file: UploadFile = File(...),
    token: dict = Depends(verify_firebase_token),
):
    uid = token["uid"]

    # Read and validate file
    image_bytes = await file.read()
    if len(image_bytes) > _MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")

    # OCR → parse → normalize
    raw_text = ocr_service.extract_text(image_bytes)
    parsed_names = receipt_parser.parse(raw_text)
    normalized_names = [normalizer.normalize(name) for name in parsed_names]

    # Write to Firestore and build response
    pantry_ref = db.collection("users").document(uid).collection("pantry")
    items: list[PantryItem] = []

    for name in normalized_names:
        doc_ref = pantry_ref.document()
        item_data = {"name": name, "quantity": 1.0, "unit": ""}
        doc_ref.set(item_data)
        items.append(PantryItem(id=doc_ref.id, **item_data))

    return ReceiptUploadResponse(raw_text=raw_text, parsed_items=items)
