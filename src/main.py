import os
from dotenv import load_dotenv
from fastapi import FastAPI
from src.routes.report_routes import router

# Cargar configuración del archivo .env
load_dotenv()

app = FastAPI()

# Agregar las rutas
app.include_router(router)
