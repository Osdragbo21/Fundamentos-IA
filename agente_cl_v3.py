import os
import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId  # <--  Necesario para buscar por ID

# --- 1. Cargar Credenciales ---
load_dotenv()
usuario = os.getenv("MONGO_USER")
password = os.getenv("MONGO_PASSWORD")
cluster = os.getenv("MONGO_CLUSTER")
bd_nombre = os.getenv("MONGO_DB")
coleccion_nombre = os.getenv("MONGO_COLLECTION")

mongo_url = f"mongodb+srv://{usuario}:{password}@{cluster}/"
cliente = MongoClient(mongo_url)
coleccion = cliente[bd_nombre][coleccion_nombre]

# --- 2. Lógica del Agente ---
class AgenteClimatizacion:
    def __init__(self):
        self.temperatura = 0.0
        self.humedad = 0.0
        self.accion = ""

    def tomar_decision(self, temp, hum):
        self.temperatura = temp
        self.humedad = hum
        if self.temperatura > 30 and self.humedad > 70:
            self.accion = "Encender aire acondicionado (Modo Deshumidificador)"
        elif self.temperatura > 30:
            self.accion = "Encender ventilador"
        elif self.temperatura < 18:
            self.accion = "Encender calefacción"
        else:
            self.accion = "Mantener sistema apagado"
        return self.accion

# --- 3. Funciones CRUD (Crear, Leer, Actualizar, Eliminar) ---

# C: CREATE (Insertar)
def insertar_registro():
    try:
        temp = float(entry_temp.get())
        hum = float(entry_hum.get())
    except ValueError:
        messagebox.showwarning("Entrada", "Ingresa números válidos.")
        return

    agente = AgenteClimatizacion()
    decision = agente.tomar_decision(temp, hum)

    try:
        nuevo_registro = {
            "temperatura_C": temp,
            "humedad_pct": hum,
            "accion_tomada": decision,
            "tipo_registro": "clima"
        }
        coleccion.insert_one(nuevo_registro)
        messagebox.showinfo("Éxito", "Registro insertado correctamente.")
        limpiar_formulario()
        consultar_registros()
    except Exception as e:
        messagebox.showerror("Error", f"Fallo al insertar:\n{e}")

# R: READ (Consultar)
def consultar_registros():
    try:
        # Ya NO ocultamos el _id
        documentos = list(coleccion.find({"tipo_registro": "clima"}))
        
        for item in tabla.get_children():
            tabla.delete(item)
            
        for doc in documentos:
            # Extraemos el _id y lo convertimos a texto para la tabla
            valores = (str(doc["_id"]), doc.get("temperatura_C", ""), doc.get("humedad_pct", ""), doc.get("accion_tomada", ""))
            tabla.insert("", "end", values=valores)
    except Exception as e:
        messagebox.showerror("Error", f"Error al consultar:\n{e}")

# U: UPDATE (Actualizar)
def preparar_edicion(event):
    """Carga los datos de la fila seleccionada en las cajas de texto"""
    seleccion = tabla.selection()
    if not seleccion:
        return
    
    item = tabla.item(seleccion[0])
    valores = item['values']
    
    # Llenar cajas de texto con los valores de la tabla
    limpiar_formulario()
    entry_temp.insert(0, valores[1])
    entry_hum.insert(0, valores[2])
    
    # Guardamos el ID temporalmente en un label oculto para saber qué editar
    lbl_id_oculto.config(text=valores[0])
    lbl_estado.config(text="Modo: EDITANDO REGISTRO", fg="orange")

def actualizar_registro():
    id_mongo = lbl_id_oculto.cget("text")
    if not id_mongo:
        messagebox.showwarning("Aviso", "Primero selecciona un registro de la tabla para editar.")
        return
        
    try:
        temp = float(entry_temp.get())
        hum = float(entry_hum.get())
    except ValueError:
        messagebox.showwarning("Entrada", "Ingresa números válidos.")
        return

    # Recalcular la decisión del agente con los nuevos datos
    agente = AgenteClimatizacion()
    nueva_decision = agente.tomar_decision(temp, hum)

    try:
        # Instrucción UPDATE en MongoDB
        coleccion.update_one(
            {"_id": ObjectId(id_mongo)}, # Buscar por ID
            {"$set": {                   # Reemplazar estos campos
                "temperatura_C": temp,
                "humedad_pct": hum,
                "accion_tomada": nueva_decision
            }}
        )
        messagebox.showinfo("Éxito", "Registro actualizado.")
        limpiar_formulario()
        consultar_registros()
    except Exception as e:
        messagebox.showerror("Error", f"Fallo al actualizar:\n{e}")

# D: DELETE (Eliminar)
def eliminar_registro():
    seleccion = tabla.selection()
    if not seleccion:
        messagebox.showwarning("Aviso", "Selecciona un registro de la tabla para eliminar.")
        return
    
    # Obtener el ID de la fila seleccionada
    item = tabla.item(seleccion[0])
    id_mongo = item['values'][0]
    
    respuesta = messagebox.askyesno("Confirmar", "¿Estás seguro de borrar este registro?")
    if respuesta:
        try:
            # Instrucción DELETE en MongoDB
            coleccion.delete_one({"_id": ObjectId(id_mongo)})
            messagebox.showinfo("Éxito", "Registro eliminado.")
            limpiar_formulario()
            consultar_registros()
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al eliminar:\n{e}")

def limpiar_formulario():
    entry_temp.delete(0, tk.END)
    entry_hum.delete(0, tk.END)
    lbl_id_oculto.config(text="")
    lbl_estado.config(text="Modo: INSERTANDO NUEVO", fg="green")

# --- 4. Interfaz Gráfica ---
ventana = tk.Tk()
ventana.title("CRUD Agente de Climatización - Atlas")
ventana.geometry("750x550")

# Formulario
marco_form = tk.LabelFrame(ventana, text="Sensores", padx=10, pady=10)
marco_form.pack(fill="x", padx=20, pady=10)

tk.Label(marco_form, text="Temperatura (°C):").grid(row=0, column=0)
entry_temp = tk.Entry(marco_form, width=10)
entry_temp.grid(row=0, column=1, padx=5)

tk.Label(marco_form, text="Humedad (%):").grid(row=0, column=2)
entry_hum = tk.Entry(marco_form, width=10)
entry_hum.grid(row=0, column=3, padx=5)

lbl_estado = tk.Label(marco_form, text="Modo: INSERTANDO NUEVO", fg="green", font=("Arial", 9, "bold"))
lbl_estado.grid(row=0, column=4, padx=20)
lbl_id_oculto = tk.Label(marco_form, text="") # Guarda el ID de Mongo de forma invisible

# Botones CRUD
marco_botones = tk.Frame(ventana)
marco_botones.pack(pady=10)

tk.Button(marco_botones, text="Insertar Nuevo", bg="lightgreen", command=insertar_registro).grid(row=0, column=0, padx=5)
tk.Button(marco_botones, text="Actualizar Seleccionado", bg="lightblue", command=actualizar_registro).grid(row=0, column=1, padx=5)
tk.Button(marco_botones, text="Eliminar Seleccionado", bg="salmon", command=eliminar_registro).grid(row=0, column=2, padx=5)
tk.Button(marco_botones, text="Limpiar Cajas", command=limpiar_formulario).grid(row=0, column=3, padx=5)

# Tabla
marco_tabla = tk.Frame(ventana)
marco_tabla.pack(expand=True, fill="both", padx=20, pady=10)

# Agregamos la columna ID (la ocultamos visualmente para que se vea limpio, pero el código la lee)
columnas = ("ID", "Temperatura", "Humedad", "Acción Tomada")
tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", displaycolumns=("Temperatura", "Humedad", "Acción Tomada"))

tabla.heading("Temperatura", text="Temp (°C)")
tabla.heading("Humedad", text="Humedad (%)")
tabla.heading("Acción Tomada", text="Acción del Agente")

tabla.column("Temperatura", width=100, anchor="center")
tabla.column("Humedad", width=100, anchor="center")
tabla.column("Acción Tomada", width=400, anchor="w")
tabla.pack(expand=True, fill="both")

# Evento: Al hacer doble clic en una fila, cargar datos para editar
tabla.bind("<Double-1>", preparar_edicion)

consultar_registros()
ventana.mainloop()