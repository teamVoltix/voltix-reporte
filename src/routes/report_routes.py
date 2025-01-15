from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from src.models.schemas import ComparisonData
from src.services.pdf_generator import generate_pdf

router = APIRouter()

@router.post("/download_report")
async def download_report(data: ComparisonData, token: str = Depends(lambda: None)):
    try:
        # Usamos la lógica de `generate_pdf` para crear el PDF
        pdf = generate_pdf(data)
        return Response(content=pdf, media_type="application/pdf", headers={
            "Content-Disposition": "attachment; filename=report.pdf"
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servidor: {str(e)}")
