import tkinter as tk
from tkinter import ttk, messagebox
import json
import threading

# Importar nuestros módulos backend
from motor_reglas import evaluar_camion_extendido
from clasificador_ia import procesar_incidente

def evaluar_acceso():
    """Captura los datos de la pestaña de accesos, los evalúa y actualiza el semáforo."""
    placa = entry_placa.get().strip()
    operador = entry_operador.get().strip()
    
    if not placa or not operador:
        messagebox.showwarning("Datos incompletos", "Por favor ingresa la placa y el nombre del operador.")
        return

    # Obtener valores booleanos de los Checkbuttons
    P = var_P.get()
    Q = var_Q.get()
    R = var_R.get()
    S = var_S.get()
    T = var_T.get()
    U = var_U.get()

    # Ejecutar el motor de reglas (esto también guarda en MongoDB)
    resultado = evaluar_camion_extendido(placa, operador, P, Q, R, S, T, U)

    # Actualizar Interfaz (Semáforo y Explicación)
    texto_explicacion.config(state=tk.NORMAL)
    texto_explicacion.delete(1.0, tk.END)
    
    if resultado["resultado_A"]:
        lbl_semaforo.config(bg="#33cc33", text="ACCESO PERMITIDO (A)", fg="white")
    elif resultado["resultado_E"]:
        lbl_semaforo.config(bg="#ffaa00", text="INSPECCIÓN ESPECIAL (E)", fg="black")
    else:
        lbl_semaforo.config(bg="#cc3333", text="ACCESO DENEGADO", fg="white")

    for paso in resultado["explicacion_paso_a_paso"]:
        texto_explicacion.insert(tk.END, f"{paso}\n")
    
    texto_explicacion.config(state=tk.DISABLED)

def clasificar_correo():
    """Envía el texto del correo al LLM usando un hilo para no congelar la GUI."""
    correo = text_correo.get(1.0, tk.END).strip()
    if not correo:
        return
    
    btn_clasificar.config(state=tk.DISABLED, text="Analizando con IA...")
    text_resultado_ia.config(state=tk.NORMAL)
    text_resultado_ia.delete(1.0, tk.END)
    text_resultado_ia.insert(tk.END, "Procesando correo con llama3.2:1b...\n")
    text_resultado_ia.config(state=tk.DISABLED)

    def tarea_ia():
        resultado = procesar_incidente(correo)
        
        # Mostrar resultado en la GUI de forma segura
        ventana.after(0, mostrar_resultado_clasificacion, resultado)

    threading.Thread(target=tarea_ia, daemon=True).start()

def mostrar_resultado_clasificacion(resultado):
    """Actualiza la caja de texto con el JSON generado por el LLM."""
    text_resultado_ia.config(state=tk.NORMAL)
    text_resultado_ia.delete(1.0, tk.END)
    text_resultado_ia.insert(tk.END, json.dumps(resultado, indent=2, ensure_ascii=False))
    text_resultado_ia.config(state=tk.DISABLED)
    btn_clasificar.config(state=tk.NORMAL, text="Clasificar Incidente")

# --- CONSTRUCCIÓN DE LA VENTANA PRINCIPAL ---
ventana = tk.Tk()
ventana.title("LogiSmart - Panel de Control Inteligente")
ventana.geometry("850x650")
ventana.configure(bg="#f0f0f0")

# Sistema de Pestañas
notebook = ttk.Notebook(ventana)
notebook.pack(pady=10, expand=True, fill="both")

# --- PESTAÑA 1: CONTROL DE ACCESOS ---
frame_accesos = tk.Frame(notebook, bg="white")
notebook.add(frame_accesos, text="Control de Accesos Vehiculares")

# Panel Izquierdo: Formulario
frame_form = tk.LabelFrame(frame_accesos, text="Datos del Vehículo y Simulador Lógico", bg="white", padx=15, pady=15)
frame_form.pack(side=tk.LEFT, fill="y", padx=15, pady=15)

tk.Label(frame_form, text="Placa:", bg="white").pack(anchor="w")
entry_placa = tk.Entry(frame_form, width=25)
entry_placa.pack(pady=(0, 10))

tk.Label(frame_form, text="Operador en turno:", bg="white").pack(anchor="w")
entry_operador = tk.Entry(frame_form, width=25)
entry_operador.pack(pady=(0, 15))

# Variables lógicas
var_P = tk.BooleanVar()
var_Q = tk.BooleanVar()
var_R = tk.BooleanVar()
var_S = tk.BooleanVar()
var_T = tk.BooleanVar()
var_U = tk.BooleanVar()

tk.Checkbutton(frame_form, text="(P) Autorización Previa", variable=var_P, bg="white").pack(anchor="w")
tk.Checkbutton(frame_form, text="(S) Certificación de Conductor", variable=var_S, bg="white").pack(anchor="w")
tk.Checkbutton(frame_form, text="(T) Horario Permitido", variable=var_T, bg="white").pack(anchor="w")
tk.Checkbutton(frame_form, text="(U) Seguro Vigente", variable=var_U, bg="white").pack(anchor="w")
tk.Checkbutton(frame_form, text="(Q) Exceso de Peso", variable=var_Q, bg="white").pack(anchor="w")
tk.Checkbutton(frame_form, text="(R) Materiales Peligrosos", variable=var_R, bg="white").pack(anchor="w")

tk.Button(frame_form, text="Evaluar Acceso", command=evaluar_acceso, bg="#007acc", fg="white", font=("Arial", 10, "bold"), pady=5).pack(fill="x", pady=20)

# Panel Derecho: Resultados
frame_res = tk.Frame(frame_accesos, bg="white")
frame_res.pack(side=tk.RIGHT, expand=True, fill="both", padx=15, pady=15)

lbl_semaforo = tk.Label(frame_res, text="ESPERANDO VEHÍCULO", bg="gray", fg="white", font=("Arial", 14, "bold"), pady=20)
lbl_semaforo.pack(fill="x", pady=(0, 15))

tk.Label(frame_res, text="Justificación del Motor de Reglas:", bg="white", font=("Arial", 10, "bold")).pack(anchor="w")
texto_explicacion = tk.Text(frame_res, height=15, bg="#f9f9f9", font=("Consolas", 10))
texto_explicacion.pack(fill="both", expand=True)
texto_explicacion.config(state=tk.DISABLED)


# --- PESTAÑA 2: BANDEJA DE INCIDENTES (IA) ---
frame_incidentes = tk.Frame(notebook, bg="white")
notebook.add(frame_incidentes, text="Bandeja de Incidentes (LLM)")

tk.Label(frame_incidentes, text="Pega el correo del reporte operativo aquí:", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=15, pady=(15, 5))
text_correo = tk.Text(frame_incidentes, height=6, bg="#f9f9f9", font=("Arial", 11))
text_correo.pack(fill="x", padx=15)

btn_clasificar = tk.Button(frame_incidentes, text="Clasificar Incidente", command=clasificar_correo, bg="#4b0082", fg="white", font=("Arial", 10, "bold"), pady=5)
btn_clasificar.pack(pady=15)

tk.Label(frame_incidentes, text="Resultado estructurado (Guardado en MongoDB):", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", padx=15)
text_resultado_ia = tk.Text(frame_incidentes, height=12, bg="#1e1e1e", fg="#55ff55", font=("Consolas", 11))
text_resultado_ia.pack(fill="both", expand=True, padx=15, pady=(5, 15))
text_resultado_ia.config(state=tk.DISABLED)

ventana.mainloop()