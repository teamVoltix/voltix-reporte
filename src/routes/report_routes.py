from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from src.models.schemas import ComparisonData
from src.services.pdf_generator import generate_pdf
from src.services.redis_service import redis_client, cache_report, get_cached_report

router = APIRouter()

@router.post("/download_report")
async def download_report(data: ComparisonData, token: str = Depends(lambda: None)):
    try:
        # Generar una clave única para el informe (por ejemplo, basada en el usuario y el período)
        cache_key = f"report:{data.user}:{data.billing_period_start}:{data.billing_period_end}"
        
        # Verificar si ya existe un informe en caché
        cached_report = get_cached_report(cache_key)
        if cached_report:
            return Response(content=cached_report, media_type="application/pdf", headers={
                "Content-Disposition": "attachment; filename=report.pdf"
            })

        # Generar el PDF si no está en caché
        pdf = generate_pdf(data)
        
        # Guardar el PDF en el caché de Redis
        cache_report(cache_key, pdf)

        return Response(content=pdf, media_type="application/pdf", headers={
            "Content-Disposition": "attachment; filename=report.pdf"
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servidor: {str(e)}")

# Ruta de prueba para verificar la conexión a Redis
@router.get("/test_redis")
async def test_redis():
    try:
        redis_client.ping()
        return {"message": "Conexión exitosa a Redis"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo conectar a Redis: {str(e)}")
