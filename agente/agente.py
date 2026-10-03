import tkinter as tk
from tkinter import ttk, messagebox
from bson.objectid import ObjectId

# ¡Aquí ocurre la magia de la modularización! 
# Importamos la función desde nuestro propio archivo conexion.py
from conexion import obtener_coleccion

# Inicializamos la conexión a la base de datos
coleccion = obtener_coleccion()

# --- 1. Lógica del Agente ---
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

# --- 2. Funciones CRUD ---
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

def consultar_registros():
    try:
        documentos = list(coleccion.find({"tipo_registro": "clima"}))
        for item in tabla.get_children():
            tabla.delete(item)
            
        for doc in documentos:
            valores = (str(doc["_id"]), doc.get("temperatura_C", ""), doc.get("humedad_pct", ""), doc.get("accion_tomada", ""))
            tabla.insert("", "end", values=valores)
    except Exception as e:
        messagebox.showerror("Error", f"Error al consultar:\n{e}")

def preparar_edicion(event):
    seleccion = tabla.selection()
    if not seleccion: return
    
    valores = tabla.item(seleccion[0])['values']
    limpiar_formulario()
    entry_temp.insert(0, valores[1])
    entry_hum.insert(0, valores[2])
    
    lbl_id_oculto.config(text=valores[0])
    lbl_estado.config(text="Modo: EDITANDO", fg="orange")

def actualizar_registro():
    id_mongo = lbl_id_oculto.cget("text")
    if not id_mongo:
        messagebox.showwarning("Aviso", "Selecciona un registro de la tabla.")
        return
        
    try:
        temp = float(entry_temp.get())
        hum = float(entry_hum.get())
    except ValueError:
        messagebox.showwarning("Entrada", "Ingresa números válidos.")
        return

    agente = AgenteClimatizacion()
    nueva_decision = agente.tomar_decision(temp, hum)

    try:
        coleccion.update_one(
            {"_id": ObjectId(id_mongo)},
            {"$set": {"temperatura_C": temp, "humedad_pct": hum, "accion_tomada": nueva_decision}}
        )
        messagebox.showinfo("Éxito", "Registro actualizado.")
        limpiar_formulario()
        consultar_registros()
    except Exception as e:
        messagebox.showerror("Error", f"Fallo al actualizar:\n{e}")

def eliminar_registro():
    seleccion = tabla.selection()
    if not seleccion:
        messagebox.showwarning("Aviso", "Selecciona un registro.")
        return
    
    id_mongo = tabla.item(seleccion[0])['values'][0]
    
    if messagebox.askyesno("Confirmar", "¿Borrar este registro?"):
        try:
            coleccion.delete_one({"_id": ObjectId(id_mongo)})
            limpiar_formulario()
            consultar_registros()
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al eliminar:\n{e}")

def limpiar_formulario():
    entry_temp.delete(0, tk.END)
    entry_hum.delete(0, tk.END)
    lbl_id_oculto.config(text="")
    lbl_estado.config(text="Modo: INSERTANDO NUEVO", fg="green")

# --- 3. Interfaz Gráfica ---
ventana = tk.Tk()
ventana.title("Agente de Climatización (Modular)")
ventana.geometry("750x550")

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
lbl_id_oculto = tk.Label(marco_form, text="") 

marco_botones = tk.Frame(ventana)
marco_botones.pack(pady=10)
tk.Button(marco_botones, text="Insertar", bg="lightgreen", command=insertar_registro).grid(row=0, column=0, padx=5)
tk.Button(marco_botones, text="Actualizar", bg="lightblue", command=actualizar_registro).grid(row=0, column=1, padx=5)
tk.Button(marco_botones, text="Eliminar", bg="salmon", command=eliminar_registro).grid(row=0, column=2, padx=5)
tk.Button(marco_botones, text="Limpiar", command=limpiar_formulario).grid(row=0, column=3, padx=5)

marco_tabla = tk.Frame(ventana)
marco_tabla.pack(expand=True, fill="both", padx=20, pady=10)

columnas = ("ID", "Temperatura", "Humedad", "Acción Tomada")
tabla = ttk.Treeview(marco_tabla, columns=columnas, show="headings", displaycolumns=("Temperatura", "Humedad", "Acción Tomada"))

tabla.heading("Temperatura", text="Temp (°C)")
tabla.heading("Humedad", text="Humedad (%)")
tabla.heading("Acción Tomada", text="Acción del Agente")
tabla.column("Temperatura", width=100, anchor="center")
tabla.column("Humedad", width=100, anchor="center")
tabla.column("Acción Tomada", width=400, anchor="w")
tabla.pack(expand=True, fill="both")

tabla.bind("<Double-1>", preparar_edicion)

# Iniciar la consulta y la ventana
consultar_registros()
ventana.mainloop()