import os
from dotenv import load_dotenv
from pymongo import MongoClient

def obtener_coleccion():
    """
    Carga las credenciales del archivo .env, establece la conexión
    con MongoDB Atlas y devuelve la colección lista para usarse.
    """
    # 1. Cargar variables de entorno
    load_dotenv()
    usuario = os.getenv("MONGO_USER")
    password = os.getenv("MONGO_PASSWORD")
    cluster = os.getenv("MONGO_CLUSTER")
    bd_nombre = os.getenv("MONGO_DB")
    coleccion_nombre = os.getenv("MONGO_COLLECTION")

    # 2. Construir la URL
    mongo_url = f"mongodb+srv://{usuario}:{password}@{cluster}/"

    # 3. Conectar y retornar la colección
    cliente = MongoClient(mongo_url)
    coleccion = cliente[bd_nombre][coleccion_nombre]
    
    return coleccion

# Pequeña prueba para verificar que funciona si ejecutamos este archivo directamente
if __name__ == "__main__":
    try:
        col = obtener_coleccion()
        print(f"¡Conexión exitosa a la base de datos!")
    except Exception as e:
        print(f"Error al conectar: {e}")