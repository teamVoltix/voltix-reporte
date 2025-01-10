from fastapi import FastAPI
from src.routes.report_routes import router as report_router

app = FastAPI()

# Registrar las rutas
app.include_router(report_router)
