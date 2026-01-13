import os
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status

from controllers.auth_controller import get_current_admin
from schemas.auth_schema import UserPublic

router = APIRouter(tags=["Uploads"])


def _uploads_dir() -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_dir, "uploads")


@router.post("/products", status_code=status.HTTP_201_CREATED)
async def upload_product_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: UserPublic = Depends(get_current_admin),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se permiten archivos de imagen.",
        )

    _, ext = os.path.splitext(file.filename or "")
    ext = ext.lower() if ext else ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    upload_dir = _uploads_dir()
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, filename)

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Archivo vacio.")

    with open(filepath, "wb") as handle:
        handle.write(content)

    base = str(request.base_url).rstrip("/")
    return {"url": f"{base}/uploads/{filename}"}
