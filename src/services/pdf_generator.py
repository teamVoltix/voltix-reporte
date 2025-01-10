from weasyprint import HTML
from fastapi import HTTPException
from datetime import datetime

def generate_pdf(data):
    try:
        # Convertir las cadenas de fechas en objetos datetime
        billing_period_start = datetime.fromisoformat(data.billing_period_start)
        billing_period_end = datetime.fromisoformat(data.billing_period_end)

        # Preparar los datos para el reporte
        billing_period = {
            "status": "Sin discrepancia" if data.is_comparison_valid else "Con discrepancia",
            "invoice_start_date": billing_period_start.strftime("%Y-%m-%d"),
            "invoice_end_date": billing_period_end.strftime("%Y-%m-%d"),
            "measurement_start_date": data.measurement_start,
            "measurement_end_date": data.measurement_end,
            "days_billed": (billing_period_end - billing_period_start).days,
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

        # Renderizar el HTML
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
        pdf = HTML(string=html_template).write_pdf()
        return pdf

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte: {str(e)}")
