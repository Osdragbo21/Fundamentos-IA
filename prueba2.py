import os
from dotenv import load_dotenv
from pymongo import MongoClient

# 1. Cargar las variables ocultas del archivo .env
load_dotenv()

# 2. Asignar los valores a variables de Python
usuario = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASSWORD")
cluster = os.getenv("MONGO_CLUSTER")
bd_nombre = os.getenv("MONGO_DB")
coleccion_nombre = os.getenv("MONGO_COLLECTION")

# 3. Construir la mongo_url armando las piezas
mongo_url = f"mongodb+srv://{usuario}:{password}@{cluster}/"

# 4. Conectarse a Atlas
try:
    cliente = MongoClient(mongo_url)
    db = cliente[bd_nombre]
    coleccion = db[coleccion_nombre]
    
    # Inserción de prueba para validar que funciona
    coleccion.insert_one({"mensaje": "¡Conexión exitosa a Atlas!", "tipo": "prueba"})
    print(f"¡Conectado exitosamente a la base de datos '{bd_nombre}' en el clúster!")
    
except Exception as e:
    print("Error al conectar:", e)