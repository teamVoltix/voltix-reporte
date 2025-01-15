from fastapi import FastAPI
from src.routes.report_routes import router

# Crea la aplicación FastAPI
app = FastAPI()

# Incluye las rutas
app.include_router(router)
