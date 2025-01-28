import redis
from dotenv import load_dotenv
import os

# Cargar las variables del archivo .env
load_dotenv()

# Obtener configuraciones desde el entorno
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Configurar la conexión con Redis
redis_client = redis.StrictRedis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=False  # Cambié esto a False para tratar datos binarios
)

# Funciones de ejemplo para interactuar con Redis
def cache_report(key: str, value: bytes, expiration: int = 3600):
    """
    Guarda un informe en Redis con una clave y un tiempo de expiración.
    """
    redis_client.set(key, value, ex=expiration)

def get_cached_report(key: str) -> bytes:
    """
    Recupera un informe en caché de Redis.
    """
    result = redis_client.get(key)
    return result if result else None
