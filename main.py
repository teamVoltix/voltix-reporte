from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, ValidationError
from weasyprint import HTML
from typing import Dict
from datetime import datetime

# Crear la aplicación FastAPI
app = FastAPI()

# Modelo Pydantic para validar el JSON recibido
class ComparisonData(BaseModel):
    user: str
    billing_period_start: str
    billing_period_end: str
    measurement_start: str
    measurement_end: str
    comparison_results: Dict
    is_comparison_valid: bool

# Endpoint para descargar el reporte
@app.post("/download_report")
async def download_report(data: ComparisonData):  # Validamos el JSON enviado en el cuerpo
    try:
        # Preparar datos para el reporte
        billing_period = {
            "status": "Sin discrepancia" if data.is_comparison_valid else "Con discrepancia",
            "invoice_start_date": data.billing_period_start,
            "invoice_end_date": data.billing_period_end,
            "measurement_start_date": data.measurement_start,
            "measurement_end_date": data.measurement_end,
            "days_billed": (
                (datetime.fromisoformat(data.billing_period_end) - datetime.fromisoformat(data.billing_period_start)).days
            ),
        }
        comparison_results = data.comparison_results
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

    except ValidationError as e:
        raise HTTPException(status_code=400, detail="Datos inválidos")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error del servidor: {str(e)}")
