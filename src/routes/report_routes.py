from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from src.models.schemas import ComparisonData
from src.services.pdf_generator import generate_pdf

router = APIRouter()

@router.post("/download_report")
async def download_report(data: ComparisonData):  # Validamos el JSON enviado en el cuerpo
    try:
        pdf = generate_pdf(data)
        return Response(content=pdf, media_type="application/pdf", headers={
            "Content-Disposition": "attachment; filename=report.pdf"
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servidor: {str(e)}")
