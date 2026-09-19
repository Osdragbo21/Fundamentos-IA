import os
import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv
from pymongo import MongoClient
from pyspark.sql import SparkSession

# Cargar credenciales
load_dotenv()
usuario = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASSWORD")
cluster = os.getenv("MONGO_CLUSTER")
bd_nombre = os.getenv("MONGO_DB")
coleccion_nombre = os.getenv("MONGO_COLLECTION")

def cargar_datos():
    try:
        # 1. Conectar a MongoDB Atlas
        mongo_url = f"mongodb+srv://{usuario}:{password}@{cluster}/"
        cliente = MongoClient(mongo_url)
        coleccion = cliente[bd_nombre][coleccion_nombre]
        
        documentos = list(coleccion.find({}, {"_id": 0}))
        
        if not documentos:
            messagebox.showinfo("Aviso", "La colección está vacía.")
            return

        # 2. Procesar con PySpark
        spark = SparkSession.builder.appName("TkinterSpark").getOrCreate()
        df = spark.createDataFrame(documentos)
        
        # 3. Limpiar la tabla visual antes de insertar nuevos datos
        for item in tabla.get_children():
            tabla.delete(item)
            
        # 4. Configurar las columnas en Tkinter basándose en Spark
        columnas = df.columns
        tabla["columns"] = columnas
        tabla["show"] = "headings" # Ocultar la primera columna vacía
        
        for col in columnas:
            tabla.heading(col, text=col.capitalize())
            tabla.column(col, width=120, anchor="center")
            
        # 5. Extraer datos de Spark e insertarlos en la interfaz
        filas = df.collect()
        for fila in filas:
            # Convertir la fila de Spark en una lista de valores
            valores = [fila[c] for c in columnas]
            tabla.insert("", "end", values=valores)
            
    except Exception as e:
        messagebox.showerror("Error de Conexión", f"Ocurrió un problema:n{e}")

# --- Configuración de la Ventana Principal ---
ventana = tk.Tk()
ventana.title("Visualizador de Datos: Atlas + PySpark")
ventana.geometry("600x400")

# Botón de acción
btn_cargar = tk.Button(ventana, text="Cargar Datos desde la Nube", command=cargar_datos, font=("Arial", "11", "bold"))
btn_cargar.pack(pady=15)

# Marco y Tabla (Treeview)
marco_tabla = tk.Frame(ventana)
marco_tabla.pack(expand=True, fill="both", padx=20, pady=10)

tabla = ttk.Treeview(marco_tabla)
tabla.pack(expand=True, fill="both")

# Iniciar la interfaz
ventana.mainloop()
