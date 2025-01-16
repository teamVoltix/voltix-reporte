'''from jose import jwt, JWTError
from fastapi import HTTPException
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# Cargar configuración del archivo .env
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")  # Cargamos la clave secreta del archivo .env
ALGORITHM = "HS256"  # Asegúrate de que el backend use este algoritmo

def verify_jwt(token: str):
    try:
        if not SECRET_KEY:
            raise HTTPException(status_code=500, detail="SECRET_KEY no configurada en el entorno.")
        
        # Decodificar el token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verificar si el token ha expirado
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(tz=timezone.utc):
            raise HTTPException(status_code=401, detail="Token expirado")

        # Puedes validar otros claims aquí, como `iss` o `aud`
        return payload
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Token inválido") from e
