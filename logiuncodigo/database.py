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

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "logismart_db"

def get_database():
    """Establece y verifica la conexión con MongoDB."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Forzar una llamada para verificar la conexión real
        client.admin.command('ping')
        log.info("Conexión exitosa a MongoDB.")
        return client[DB_NAME]
    except ConnectionFailure:
        log.error("Error crítico: No se pudo conectar a MongoDB. Verifica tu clúster o URI.")
        return None

# Instancia global exportable de la base de datos
db = get_database()

# Colecciones disponibles
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