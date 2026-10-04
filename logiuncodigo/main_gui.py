import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import threading

# Importar módulos backend
from motor_reglas import evaluar_camion_extendido
from clasificador_ia import procesar_incidente
from database import accesos_col, incidentes_col  # Importación crucial para RAG
import ollama

# ==========================================
# FUNCIONES LÓGICAS Y DE CONTROL
# ==========================================
def evaluar_acceso():
    placa = entry_placa.get().strip()
    operador = entry_operador.get().strip()
    
    if not placa or not operador:
        messagebox.showwarning("Datos incompletos", "Por favor ingresa la placa y el nombre del operador.")
        return

    P, Q, R = var_P.get(), var_Q.get(), var_R.get()
    S, T, U = var_S.get(), var_T.get(), var_U.get()

    resultado = evaluar_camion_extendido(placa, operador, P, Q, R, S, T, U)

    texto_explicacion.config(state=tk.NORMAL)
    texto_explicacion.delete(1.0, tk.END)
    
    if resultado["resultado_A"]:
        lbl_semaforo.config(bg="#16A34A", text="ACCESO PERMITIDO (A)", fg="white")
    elif resultado["resultado_E"]:
        lbl_semaforo.config(bg="#F59E0B", text="INSPECCIÓN ESPECIAL (E)", fg="white")
    else:
        lbl_semaforo.config(bg="#DC2626", text="ACCESO DENEGADO", fg="white")

    for paso in resultado["explicacion_paso_a_paso"]:
        texto_explicacion.insert(tk.END, f"{paso}\n")
    texto_explicacion.config(state=tk.DISABLED)

def cargar_ejemplo_correo():
    text_correo.delete(1.0, tk.END)
    ejemplo = "URGENTE: Reporto que la unidad con placas LUN-2026 tuvo un percance. Al intentar maniobrar en el Andén Sur, se le ponchó una llanta y está bloqueando el paso de los demás camiones. Necesitamos soporte de mantenimiento de inmediato."
    text_correo.insert(tk.END, ejemplo)

def clasificar_correo():
    correo = text_correo.get(1.0, tk.END).strip()
    if not correo:
        messagebox.showinfo("Bandeja vacía", "Pega un reporte o usa el botón 'Cargar Reporte de Ejemplo'.")
        return
    
    btn_clasificar.config(state=tk.DISABLED, text="Analizando reporte con IA...")
    lbl_ai_estado.config(text="Procesando lectura con Llama3.2:1b...", fg="#2563EB")
    
    lbl_ai_clasificacion.config(text="--", fg="black")
    lbl_ai_prioridad.config(text="--", fg="black")
    lbl_ai_placa.config(text="--")
    lbl_ai_ubicacion.config(text="--")
    
    text_json_crudo.config(state=tk.NORMAL)
    text_json_crudo.delete(1.0, tk.END)
    text_json_crudo.config(state=tk.DISABLED)

    def tarea_ia():
        resultado = procesar_incidente(correo)
        ventana.after(0, mostrar_resultado_clasificacion, resultado)

    threading.Thread(target=tarea_ia, daemon=True).start()

def mostrar_resultado_clasificacion(resultado):
    lbl_ai_estado.config(text="Análisis completado. Datos extraídos y guardados en MongoDB.", fg="#16A34A")
    lbl_ai_clasificacion.config(text=resultado.get("clasificacion", "Desconocido"))
    
    prioridad = resultado.get("prioridad", "Media")
    color_prioridad = "#DC2626" if prioridad == "Alta" else "#F59E0B" if prioridad == "Media" else "#16A34A"
    lbl_ai_prioridad.config(text=prioridad, fg=color_prioridad)
    
    datos = resultado.get("datos_extraidos", {})
    lbl_ai_placa.config(text=datos.get("placa", "No mencionada"))
    lbl_ai_ubicacion.config(text=datos.get("ubicacion", "No mencionada"))

    text_json_crudo.config(state=tk.NORMAL)
    text_json_crudo.insert(tk.END, json.dumps(resultado, indent=2, ensure_ascii=False, default=str))
    text_json_crudo.config(state=tk.DISABLED)
    btn_clasificar.config(state=tk.NORMAL, text="Procesar Incidente")

# --- NUEVAS FUNCIONES RAG ---
def enviar_pregunta_rag(event=None):
    pregunta = entry_rag.get().strip()
    if not pregunta:
        return

    # Mostrar pregunta en el chat
    chat_rag.config(state=tk.NORMAL)
    chat_rag.insert(tk.END, f"👤 Operador: ", "user_name")
    chat_rag.insert(tk.END, f"{pregunta}\n\n", "user")
    chat_rag.config(state=tk.DISABLED)
    chat_rag.see(tk.END)
    
    entry_rag.delete(0, tk.END)
    btn_enviar_rag.config(state=tk.DISABLED, text="Consultando BD...")
    entry_rag.config(state=tk.DISABLED)

    def tarea_rag():
        try:
            # 1. Recuperación de datos desde MongoDB (Excluimos el _id para evitar errores de parseo en la IA)
            ultimos_accesos = list(accesos_col.find({}, {"_id": 0}).sort("marca_tiempo", -1).limit(5)) if accesos_col is not None else []
            ultimos_incidentes = list(incidentes_col.find({}, {"_id": 0}).sort("fecha_reporte", -1).limit(5)) if incidentes_col is not None else []

            # 2. Construir el contexto en formato texto
            contexto_bd = f"Últimos 5 accesos registrados:\n{ultimos_accesos}\n\nÚltimos 5 incidentes registrados:\n{ultimos_incidentes}"
            
            # 3. Armar el Prompt Híbrido (RAG)
            prompt = f"""Eres el Asistente RAG de LogiSmart. 
            Responde a la pregunta del operador basándote ÚNICAMENTE en el siguiente contexto extraído en tiempo real de MongoDB.
            Si la respuesta no está en el contexto, indica claramente que no tienes registros sobre eso. Sé conciso y profesional.
            
            [CONTEXTO MONGODB]:
            {contexto_bd}
            
            [PREGUNTA DEL OPERADOR]: {pregunta}
            """
            
            # 4. Llamada al LLM
            respuesta = ollama.chat(model="llama3.2:1b", messages=[{"role": "user", "content": prompt}])
            texto_respuesta = respuesta["message"]["content"]
            
        except Exception as e:
            texto_respuesta = f"Error al conectar con la base de datos o el modelo IA: {e}"

        ventana.after(0, mostrar_respuesta_rag, texto_respuesta)

    threading.Thread(target=tarea_rag, daemon=True).start()

def mostrar_respuesta_rag(respuesta):
    chat_rag.config(state=tk.NORMAL)
    chat_rag.insert(tk.END, f"🤖 LogiSmart AI: ", "ai_name")
    chat_rag.insert(tk.END, f"{respuesta}\n\n", "ai")
    chat_rag.config(state=tk.DISABLED)
    chat_rag.see(tk.END)
    
    btn_enviar_rag.config(state=tk.NORMAL, text="Enviar Consulta")
    entry_rag.config(state=tk.NORMAL)
    entry_rag.focus()

# ==========================================
# CONFIGURACIÓN VISUAL Y VENTANA MAXIMIZADA
# ==========================================
ventana = tk.Tk()
ventana.title("LogiSmart - Centro de Control Inteligente")

try:
    ventana.attributes('-zoomed', True)
except:
    ventana.state('zoomed')

ventana.configure(bg="#F4F6F9")

estilo = ttk.Style()
estilo.theme_use("clam")
estilo.configure("TNotebook", background="#F4F6F9", borderwidth=0)
estilo.configure("TNotebook.Tab", font=("Segoe UI", 11, "bold"), padding=[15, 5], background="#E2E8F0")
estilo.map("TNotebook.Tab", background=[("selected", "#FFFFFF")], foreground=[("selected", "#2563EB")])

notebook = ttk.Notebook(ventana)
notebook.pack(pady=15, padx=15, expand=True, fill="both")

FONT_TITLE = ("Segoe UI", 12, "bold")
FONT_NORM = ("Segoe UI", 11)

# ==========================================
# PESTAÑA 1: CONTROL DE ACCESOS
# ==========================================
frame_accesos = tk.Frame(notebook, bg="#F4F6F9")
notebook.add(frame_accesos, text="Control de Accesos Vehiculares")

paned_accesos = tk.PanedWindow(frame_accesos, orient=tk.HORIZONTAL, bg="#E2E8F0", sashwidth=5)
paned_accesos.pack(fill="both", expand=True)

frame_form = tk.Frame(paned_accesos, bg="#FFFFFF", padx=20, pady=20)
paned_accesos.add(frame_form, minsize=400)

tk.Label(frame_form, text="Formulario de Ingreso", font=FONT_TITLE, bg="#FFFFFF", fg="#1E293B").pack(anchor="w", pady=(0,15))
tk.Label(frame_form, text="Placa del Vehículo:", font=FONT_NORM, bg="#FFFFFF").pack(anchor="w")
entry_placa = tk.Entry(frame_form, font=FONT_NORM, width=30, bg="#F8FAFC", relief=tk.SOLID, borderwidth=1)
entry_placa.pack(pady=(2, 15), ipady=4, anchor="w")

tk.Label(frame_form, text="Operador en turno:", font=FONT_NORM, bg="#FFFFFF").pack(anchor="w")
entry_operador = tk.Entry(frame_form, font=FONT_NORM, width=30, bg="#F8FAFC", relief=tk.SOLID, borderwidth=1)
entry_operador.pack(pady=(2, 20), ipady=4, anchor="w")

tk.Label(frame_form, text="Evaluación Lógica de Requisitos:", font=FONT_TITLE, bg="#FFFFFF", fg="#1E293B").pack(anchor="w", pady=(0,10))

var_P, var_Q, var_R = tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()
var_S, var_T, var_U = tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()

opciones_logicas = [
    ("(P) Autorización Previa", var_P), ("(S) Certificación de Conductor", var_S),
    ("(T) Horario Permitido", var_T), ("(U) Seguro Vigente", var_U),
    ("(Q) Exceso de Peso", var_Q), ("(R) Materiales Peligrosos", var_R)
]

for texto, variable in opciones_logicas:
    tk.Checkbutton(frame_form, text=texto, variable=variable, font=FONT_NORM, bg="#FFFFFF", activebackground="#FFFFFF", cursor="hand2").pack(anchor="w", pady=2)

btn_evaluar = tk.Button(frame_form, text="Evaluar Vehículo", command=evaluar_acceso, font=("Segoe UI", 11, "bold"), bg="#2563EB", fg="white", relief=tk.FLAT, cursor="hand2")
btn_evaluar.pack(fill="x", pady=25, ipady=8)

frame_res = tk.Frame(paned_accesos, bg="#F8FAFC", padx=20, pady=20)
paned_accesos.add(frame_res, minsize=400)

tk.Label(frame_res, text="Estado de Acceso (Semáforo)", font=FONT_TITLE, bg="#F8FAFC").pack(anchor="w")
lbl_semaforo = tk.Label(frame_res, text="ESPERANDO VEHÍCULO...", font=("Segoe UI", 16, "bold"), bg="#94A3B8", fg="white", pady=15)
lbl_semaforo.pack(fill="x", pady=(10, 20))

tk.Label(frame_res, text="Justificación del Sistema (Trazabilidad):", font=FONT_TITLE, bg="#F8FAFC").pack(anchor="w")
texto_explicacion = tk.Text(frame_res, bg="#FFFFFF", fg="#334155", font=("Consolas", 11), relief=tk.SOLID, borderwidth=1, padx=10, pady=10)
texto_explicacion.pack(fill="both", expand=True, pady=(5,0))
texto_explicacion.config(state=tk.DISABLED)

# ==========================================
# PESTAÑA 2: BANDEJA DE INCIDENTES (IA)
# ==========================================
frame_ia = tk.Frame(notebook, bg="#F4F6F9")
notebook.add(frame_ia, text="Análisis de Incidentes (IA)")

paned_ia = tk.PanedWindow(frame_ia, orient=tk.HORIZONTAL, bg="#E2E8F0", sashwidth=5)
paned_ia.pack(fill="both", expand=True)

frame_ia_in = tk.Frame(paned_ia, bg="#FFFFFF", padx=20, pady=20)
paned_ia.add(frame_ia_in, minsize=400)

tk.Label(frame_ia_in, text="Bandeja de Entrada del Operador", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#1E293B").pack(anchor="w", pady=(0, 5))
tk.Label(frame_ia_in, text="Texto original enviado por los guardias o personal de almacén:", font=FONT_NORM, bg="#FFFFFF", fg="#64748B").pack(anchor="w", pady=(0, 10))

btn_ejemplo = tk.Button(frame_ia_in, text="Cargar Reporte de Ejemplo", command=cargar_ejemplo_correo, font=("Segoe UI", 9), bg="#E2E8F0", fg="#1E293B", relief=tk.FLAT, cursor="hand2")
btn_ejemplo.pack(anchor="w", pady=(0, 10), ipady=3, ipadx=10)

text_correo = tk.Text(frame_ia_in, bg="#F8FAFC", font=FONT_NORM, relief=tk.SOLID, borderwidth=1, padx=10, pady=10)
text_correo.pack(fill="both", expand=True)

btn_clasificar = tk.Button(frame_ia_in, text="Procesar Incidente con IA", command=clasificar_correo, font=("Segoe UI", 11, "bold"), bg="#4F46E5", fg="white", relief=tk.FLAT, cursor="hand2")
btn_clasificar.pack(fill="x", pady=(20, 0), ipady=8)

frame_ia_out = tk.Frame(paned_ia, bg="#F8FAFC", padx=20, pady=20)
paned_ia.add(frame_ia_out, minsize=400)

tk.Label(frame_ia_out, text="Extracción Inteligente de Datos", font=("Segoe UI", 14, "bold"), bg="#F8FAFC", fg="#1E293B").pack(anchor="w", pady=(0, 5))
lbl_ai_estado = tk.Label(frame_ia_out, text="Esperando reporte...", font=("Segoe UI", 10, "italic"), bg="#F8FAFC", fg="#64748B")
lbl_ai_estado.pack(anchor="w", pady=(0, 20))

frame_grid = tk.Frame(frame_ia_out, bg="#F8FAFC")
frame_grid.pack(fill="x")

tk.Label(frame_grid, text="Categoría Identificada:", font=FONT_NORM, bg="#F8FAFC", fg="#64748B").grid(row=0, column=0, sticky="w", pady=5, padx=(0,10))
lbl_ai_clasificacion = tk.Label(frame_grid, text="--", font=("Segoe UI", 12, "bold"), bg="#F8FAFC", fg="#0F172A")
lbl_ai_clasificacion.grid(row=0, column=1, sticky="w", pady=5)

tk.Label(frame_grid, text="Prioridad Sugerida:", font=FONT_NORM, bg="#F8FAFC", fg="#64748B").grid(row=1, column=0, sticky="w", pady=5, padx=(0,10))
lbl_ai_prioridad = tk.Label(frame_grid, text="--", font=("Segoe UI", 12, "bold"), bg="#F8FAFC")
lbl_ai_prioridad.grid(row=1, column=1, sticky="w", pady=5)

tk.Label(frame_grid, text="Placa Extraída:", font=FONT_NORM, bg="#F8FAFC", fg="#64748B").grid(row=2, column=0, sticky="w", pady=5, padx=(0,10))
lbl_ai_placa = tk.Label(frame_grid, text="--", font=FONT_TITLE, bg="#F8FAFC", fg="#0F172A")
lbl_ai_placa.grid(row=2, column=1, sticky="w", pady=5)

tk.Label(frame_grid, text="Ubicación Extraída:", font=FONT_NORM, bg="#F8FAFC", fg="#64748B").grid(row=3, column=0, sticky="w", pady=5, padx=(0,10))
lbl_ai_ubicacion = tk.Label(frame_grid, text="--", font=FONT_TITLE, bg="#F8FAFC", fg="#0F172A")
lbl_ai_ubicacion.grid(row=3, column=1, sticky="w", pady=5)

tk.Label(frame_ia_out, text="Estructura JSON (Para MongoDB):", font=("Segoe UI", 10, "bold"), bg="#F8FAFC", fg="#64748B").pack(anchor="w", pady=(30, 5))
text_json_crudo = tk.Text(frame_ia_out, height=10, bg="#1E293B", fg="#A7F3D0", font=("Consolas", 10), relief=tk.FLAT, padx=10, pady=10)
text_json_crudo.pack(fill="both", expand=True)
text_json_crudo.config(state=tk.DISABLED)

# ==========================================
# PESTAÑA 3: ASISTENTE RAG (CHAT MONGODB)
# ==========================================
frame_rag_tab = tk.Frame(notebook, bg="#FFFFFF", padx=20, pady=20)
notebook.add(frame_rag_tab, text="Asistente RAG (Consultas BD)")

tk.Label(frame_rag_tab, text="Consulta a la Base de Datos con Lenguaje Natural", font=("Segoe UI", 14, "bold"), bg="#FFFFFF", fg="#1E293B").pack(anchor="w", pady=(0, 5))
tk.Label(frame_rag_tab, text="Haz preguntas sobre los accesos o incidentes recientes (ej. '¿Qué pasó con el camión sab-2026?')", font=FONT_NORM, bg="#FFFFFF", fg="#64748B").pack(anchor="w", pady=(0, 15))

# Área de Chat
chat_rag = scrolledtext.ScrolledText(frame_rag_tab, font=FONT_NORM, bg="#F8FAFC", fg="#0F172A", relief=tk.SOLID, borderwidth=1, padx=15, pady=15)
chat_rag.pack(fill="both", expand=True, pady=(0, 15))

chat_rag.tag_config("user_name", foreground="#2563EB", font=("Segoe UI", 11, "bold"))
chat_rag.tag_config("user", foreground="#1E293B")
chat_rag.tag_config("ai_name", foreground="#059669", font=("Segoe UI", 11, "bold"))
chat_rag.tag_config("ai", foreground="#1E293B")
chat_rag.config(state=tk.DISABLED)

# Controles de Input
frame_rag_input = tk.Frame(frame_rag_tab, bg="#FFFFFF")
frame_rag_input.pack(fill="x")

entry_rag = tk.Entry(frame_rag_input, font=FONT_NORM, bg="#F8FAFC", relief=tk.SOLID, borderwidth=1)
entry_rag.pack(side=tk.LEFT, fill="x", expand=True, ipady=6, padx=(0, 10))
entry_rag.bind("<Return>", enviar_pregunta_rag)

btn_enviar_rag = tk.Button(frame_rag_input, text="Enviar Consulta", command=enviar_pregunta_rag, font=("Segoe UI", 11, "bold"), bg="#2563EB", fg="white", relief=tk.FLAT, cursor="hand2")
btn_enviar_rag.pack(side=tk.RIGHT, ipady=4, ipadx=10)

ventana.mainloop()