from fastapi import APIRouter, HTTPException, Header, Depends
from fastapi.responses import Response
from src.models.schemas import ComparisonData
from src.services.pdf_generator import generate_pdf
from src.services.auth import verify_jwt

router = APIRouter()

@router.post("/download_report")
async def download_report(
    data: ComparisonData,
    authorization: str = Header(...),  # JWT esperado en el header Authorization
):
    # Extraer el token del encabezado y verificarlo
    token = authorization.split(" ")[1]  # Se espera formato "Bearer <token>"
    user_data = verify_jwt(token)  # Esto lanza una excepción si el token no es válido

    try:
        pdf = generate_pdf(data)
        return Response(content=pdf, media_type="application/pdf", headers={
            "Content-Disposition": "attachment; filename=report.pdf"
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servidor: {str(e)}")
