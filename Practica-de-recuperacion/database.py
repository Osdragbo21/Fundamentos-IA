import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("logismart_db")

# Cargar variables de entorno
load_dotenv()

# Leer credenciales
USER = os.getenv("MONGO_USER")
PASSWORD = os.getenv("MONGO_PASSWORD")
CLUSTER = os.getenv("MONGO_CLUSTER")
DB_NAME = os.getenv("MONGO_DB")

def get_database():
    """Establece y verifica la conexión con MongoDB Atlas."""
    # Verificación de seguridad
    if not all([USER, PASSWORD, CLUSTER, DB_NAME]):
        log.warning("Faltan variables de entorno. Verifica tu archivo .env")
        return None
        
    MONGO_URI = f"mongodb+srv://{USER}:{PASSWORD}@{CLUSTER}/?retryWrites=true&w=majority"
    
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        # Forzar una llamada para verificar la conexión real
        client.admin.command('ping')
        log.info(f"Conexión exitosa a MongoDB Atlas. DB: {DB_NAME}")
        return client[DB_NAME]
    except Exception as e:
        log.error(f"Error crítico conectando a MongoDB: {e}")
        return None

# Instancia global exportable
db = get_database()

# Definición segura de las colecciones
camiones_col = db["camiones"] if db is not None else None
accesos_col = db["accesos"] if db is not None else None
incidentes_col = db["incidentes"] if db is not None else None
riesgos_col = db["riesgos_eticos"] if db is not None else None
evaluaciones_col = db["evaluaciones_llm"] if db is not None else None

def obtener_incidentes_por_categoria_y_semana():
    """Consulta de agregación: Agrupa incidentes por categoría."""
    if incidentes_col is None:
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