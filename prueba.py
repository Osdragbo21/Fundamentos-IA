from pymongo import MongoClient
from pyspark.sql import SparkSession

# 1. Conexión a MongoDB
cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["veterinaria_db"]
coleccion = db["pacientes"]

# Limpiar la colección por si haces la prueba varias veces
coleccion.delete_many({})

# Insertar datos de prueba
datos_prueba = [
    {"nombre": "Ami", "especie": "Perro", "raza": "Dachshund", "edad": 3},
    {"nombre": "Michi", "especie": "Gato", "raza": "Naranjoso", "edad": 2},
    {"nombre": "Toby", "especie": "Perro", "raza": "Pug", "edad": 5},
    {"nombre": "Toby", "especie": "Perro", "raza": "Pug", "edad": 8}
]
coleccion.insert_many(datos_prueba)
print("\n[Éxito] ¡Datos guardados en MongoDB local!")

# Extraer los datos (Omitimos el '_id' porque Spark requiere un formato estricto)
documentos = list(coleccion.find({}, {"_id": 0}))

# 2. Inicializar Spark
spark = SparkSession.builder.appName("TestMongoSpark").getOrCreate()

# 3. Crear un DataFrame de Spark con los datos de Mongo y mostrarlo
df = spark.createDataFrame(documentos)

print("\n[Éxito] ¡Datos procesados en un DataFrame de PySpark!\n")
df.show()