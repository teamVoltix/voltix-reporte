from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import Response
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from weasyprint import HTML
import os
from dotenv import load_dotenv
import os

# Cargar las variables del archivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está configurada.")

# Crear la aplicación FastAPI
app = FastAPI()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("La variable de entorno DATABASE_URL no está configurada.")
    
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint para descargar el reporte
@app.get("/download_report")
async def download_report(
    id: int = Query(..., description="ID de la comparación"),
    user: str = Query(..., description="Usuario autenticado"),
    db: SessionLocal = Depends(get_db)
):
    try:
        # Buscar el objeto de comparación en la base de datos usando SQL seguro
        comparison = db.execute(
            "SELECT * FROM invoice_comparison WHERE id = :id AND user = :user",
            {"id": id, "user": user}
        ).fetchone()

        if not comparison:
            raise HTTPException(status_code=404, detail="No se encontró la comparación solicitada.")

        # Preparar datos para el reporte
        billing_period = {
            "status": "Sin discrepancia" if comparison.is_comparison_valid else "Con discrepancia",
            "invoice_start_date": comparison.invoice_billing_period_start,
            "invoice_end_date": comparison.invoice_billing_period_end,
            "measurement_start_date": comparison.measurement_start,
            "measurement_end_date": comparison.measurement_end,
            "days_billed": (comparison.invoice_billing_period_end - comparison.invoice_billing_period_start).days
        }

        comparison_results = comparison.comparison_results
        consumption_details = {
            "Invoice": {
                "invoice": comparison_results['detalles_consumo']['total_consumption_kwh']['invoice'],
                "measurement": comparison_results['detalles_consumo']['total_consumption_kwh']['measurement'],
                "difference": comparison_results['detalles_consumo']['total_consumption_kwh']['difference'],
            }
        }

        total_estimated = comparison_results.get("total_a_pagar", {}).get("factura")

        # Renderizar el HTML manualmente
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Informe de Comparación</title>
        </head>
        <body>
            <h1>Informe de Comparación</h1>
            <h2>Periodo de Facturación</h2>
            <p><strong>Estado:</strong> {billing_period['status']}</p>
            <p><strong>Fecha de Inicio de la Factura:</strong> {billing_period['invoice_start_date']}</p>
            <p><strong>Fecha de Fin de la Factura:</strong> {billing_period['invoice_end_date']}</p>
            <p><strong>Comienzo periodo de Medición:</strong> {billing_period['measurement_start_date']}</p>
            <p><strong>Fin periodo de Medición:</strong> {billing_period['measurement_end_date']}</p>
            <p><strong>Días Facturados:</strong> {billing_period['days_billed']}</p>
            <h2>Detalles de Consumo</h2>
            <p><strong>Factura:</strong> {consumption_details['Invoice']['invoice']}</p>
            <p><strong>Medición:</strong> {consumption_details['Invoice']['measurement']}</p>
            <p><strong>Diferencia:</strong> {consumption_details['Invoice']['difference']}</p>
            <h2>Total Estimado</h2>
            <p><strong>Total:</strong> {total_estimated}</p>
        </body>
        </html>
        """

        # Generar PDF
        try:
            pdf = HTML(string=html_template).write_pdf()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al generar el PDF: {str(e)}")

        # Responder con el PDF
        return Response(content=pdf, media_type="application/pdf", headers={
            "Content-Disposition": "attachment; filename=report.pdf"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servidor: {str(e)}")
