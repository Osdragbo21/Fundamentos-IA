import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("logismart_db")

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Leer las credenciales desglosadas
USER = os.getenv("MONGO_USER")
PASSWORD = os.getenv("MONGO_PASSWORD")
CLUSTER = os.getenv("MONGO_CLUSTER")
DB_NAME = os.getenv("MONGO_DB")

# Construir la URI de conexión de MongoDB Atlas dinámicamente
MONGO_URI = f"mongodb+srv://{USER}:{PASSWORD}@{CLUSTER}/?retryWrites=true&w=majority"

def get_database():
    """Establece y verifica la conexión con MongoDB."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Forzar una llamada para verificar la conexión real
        client.admin.command('ping')
        log.info(f"Conexión exitosa a MongoDB. Usando base de datos: {DB_NAME}")
        return client[DB_NAME]
    except Exception as e:
        log.error(f"Error crítico: No se pudo conectar a MongoDB. Detalle: {e}")
        return None

# Instancia global exportable de la base de datos
db = get_database()

# Definición de las colecciones requeridas por el proyecto
if db is not None:
    camiones_col = db["camiones"]
    accesos_col = db["accesos"]
    incidentes_col = db["incidentes"]
    riesgos_col = db["riesgos_eticos"]
    evaluaciones_col = db["evaluaciones_llm"]

def obtener_incidentes_por_categoria_y_semana():
    """Consulta de agregación requerida: Agrupa incidentes por categoría."""
    if db is None:
        return []
    
    pipeline = [
        {"$group": {
            "_id": "$clasificacion",
            "total": {"$sum": 1},
            "incidentes": {"$push": "$$ROOT"}
        }},
        {"$sort": {"total": -1}}
    ]
    return list(incidentes_col.aggregate(pipeline))