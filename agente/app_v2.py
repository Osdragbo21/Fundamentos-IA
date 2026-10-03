import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Importamos nuestra conexión modular
from conexion import obtener_coleccion

def obtener_datos():
    """Descarga los datos directamente de Atlas"""
    coleccion = obtener_coleccion()
    return list(coleccion.find({"tipo_registro": "clima"}, {"_id": 0, "temperatura_C": 1, "humedad_pct": 1, "accion_tomada": 1}))

def mostrar_rango(accion):
    """Muestra una ventana con los rangos programados"""
    rangos = {
        "ac": "Temperatura > 30°C\n\nY\n\nHumedad > 70%",
        "vent": "Temperatura > 30°C\n\nY\n\nHumedad <= 70%",
        "calef": "Temperatura < 18°C\n\n(Sin importar la humedad)",
        "apagado": "Temperatura entre 18°C y 30°C\n\n(Sin importar la humedad)"
    }
    messagebox.showinfo("Rango Configurado", f"Condición para activar:\n\n{rangos[accion]}")

# --- Configuración de la Ventana Principal ---
ventana = tk.Tk()
ventana.title("Panel Analítico - Agente de Climatización")
ventana.geometry("800x650")

# --- Sección 1: Reglas del Agente (Botones) ---
tk.Label(ventana, text="Reglas de Decisión del Agente", font=("Arial", 14, "bold")).pack(pady=10)
tk.Label(ventana, text="Haz clic para ver las condiciones de cada respuesta").pack()

marco_botones = tk.Frame(ventana)
marco_botones.pack(pady=10)

tk.Button(marco_botones, text="❄️ Aire Acondicionado", command=lambda: mostrar_rango("ac"), bg="lightblue", width=20).grid(row=0, column=0, padx=5)
tk.Button(marco_botones, text="💨 Ventilador", command=lambda: mostrar_rango("vent"), bg="lightgreen", width=15).grid(row=0, column=1, padx=5)
tk.Button(marco_botones, text="🔥 Calefacción", command=lambda: mostrar_rango("calef"), bg="salmon", width=15).grid(row=0, column=2, padx=5)
tk.Button(marco_botones, text="⏸️ Mantener Apagado", command=lambda: mostrar_rango("apagado"), bg="lightgray", width=20).grid(row=0, column=3, padx=5)

# --- Sección 2: Gráfica de Dispersión ---
tk.Label(ventana, text="Gráfica de Decisiones (Atlas)", font=("Arial", 14, "bold")).pack(pady=10)

marco_grafica = tk.Frame(ventana)
marco_grafica.pack(expand=True, fill="both", padx=20, pady=10)

datos = obtener_datos()

if not datos:
    tk.Label(marco_grafica, text="No hay datos en la nube. Usa agente.py para insertar algunos.", fg="red").pack()
else:
    # 1. Crear la figura de Matplotlib
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # 2. Diccionario para mapear cada acción a un color distinto
    colores_map = {
        "Encender aire acondicionado (Modo Deshumidificador)": "blue",
        "Encender ventilador": "green",
        "Encender calefacción": "red",
        "Mantener sistema apagado": "gray"
    }
    
    # 3. Dibujar los puntos uno por uno
    for doc in datos:
        temp = doc.get("temperatura_C", 0)
        hum = doc.get("humedad_pct", 0)
        accion = doc.get("accion_tomada", "")
        color = colores_map.get(accion, "black")
        
        ax.scatter(temp, hum, color=color, label=accion)
        
    ax.set_xlabel("Temperatura (°C)")
    ax.set_ylabel("Humedad (%)")
    ax.set_title("Distribución de Decisiones: Temp vs Humedad")
    ax.grid(True, linestyle="--", alpha=0.6)
    
    # 4. Agrupar la leyenda para que no se repitan las etiquetas
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    if by_label:
        ax.legend(by_label.values(), by_label.keys(), loc="upper right", fontsize='small')
    
    # 5. Insertar el "lienzo" de Matplotlib dentro del marco de Tkinter
    canvas = FigureCanvasTkAgg(fig, master=marco_grafica)
    canvas.draw()
    canvas.get_tk_widget().pack(expand=True, fill="both")

ventana.mainloop()