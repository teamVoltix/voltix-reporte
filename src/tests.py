import pytest
import redis
import json
from fastapi.testclient import TestClient
from src.main import app
from src.services.redis_service import redis_client

client = TestClient(app)

# Datos de prueba
comparison_data = {
    "user": "Test User",
    "billing_period_start": "2024-01-01",
    "billing_period_end": "2024-01-31",
    "measurement_start": "2024-01-01",
    "measurement_end": "2024-01-31",
    "comparison_results": {
        "detalles_consumo": {
            "total_consumption_kwh": {
                "invoice": 100,
                "measurement": 105,
                "difference": 5
            }
        },
        "total_a_pagar": {
            "factura": 200.50
        }
    },
    "is_comparison_valid": True
}

cache_key = f"report:{comparison_data['user']}:{comparison_data['billing_period_start']}:{comparison_data['billing_period_end']}"

def test_redis_connection():
    """Verifica que Redis esté correctamente conectado."""
    try:
        redis_client.ping()
    except redis.ConnectionError:
        pytest.fail("No se pudo conectar a Redis")

def test_generate_pdf():
    """Verifica que se genere correctamente un PDF desde el microservicio."""
    response = client.post("/download_report", json=comparison_data)
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/pdf"

def test_cache_pdf():
    """Verifica que si el PDF ya está en caché, se use en lugar de generarlo nuevamente."""
    # Guardar un PDF falso en caché
    fake_pdf_content = b"%PDF-1.4 Fake PDF Content"
    redis_client.set(cache_key, fake_pdf_content, ex=3600)

    response = client.post("/download_report", json=comparison_data)
    assert response.status_code == 200
    assert response.content == fake_pdf_content  # Verifica que el contenido venga del caché
