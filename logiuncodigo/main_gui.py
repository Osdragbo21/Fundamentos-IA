import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import json
import threading
import csv
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from motor_reglas import evaluar_camion_extendido
from clasificador_ia import procesar_incidente
from database import accesos_col, incidentes_col
import ollama

# ==========================================
# FUNCIONES LÓGICAS Y DE CONTROL
# ==========================================
def evaluar_acceso():
    placa = entry_placa.get().strip()
    operador = entry_operador.get().strip()
    if not placa or not operador: return

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
        messagebox.showinfo("Bandeja vacía", "Pega un reporte antes de analizar.")
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
    lbl_ai_estado.config(text="Análisis completado. Datos guardados en MongoDB.", fg="#16A34A")
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
    btn_clasificar.config(state=tk.NORMAL, text="Procesar Incidente con IA")

def enviar_pregunta_rag(event=None):
    pregunta = entry_rag.get().strip()
    if not pregunta: return

    chat_rag.config(state=tk.NORMAL)
    chat_rag.insert(tk.END, f"Operador: ", "user_name")
    chat_rag.insert(tk.END, f"{pregunta}\n\n", "user")
    chat_rag.config(state=tk.DISABLED)
    chat_rag.see(tk.END)
    
    entry_rag.delete(0, tk.END)
    btn_enviar_rag.config(state=tk.DISABLED, text="Consultando...")
    entry_rag.config(state=tk.DISABLED)

    def tarea_rag():
        try:
            ultimos_accesos = list(accesos_col.find({}, {"_id": 0}).sort("marca_tiempo", -1).limit(5)) if accesos_col is not None else []
            ultimos_incidentes = list(incidentes_col.find({}, {"_id": 0}).sort("fecha_reporte", -1).limit(5)) if incidentes_col is not None else []
            accesos_limpios = json.dumps(ultimos_accesos, ensure_ascii=False, default=str)
            incidentes_limpios = json.dumps(ultimos_incidentes, ensure_ascii=False, default=str)
            contexto_bd = f"Últimos accesos:\n{accesos_limpios}\n\nÚltimos incidentes:\n{incidentes_limpios}"
            
            prompt = f"Eres el Asistente RAG de LogiSmart. Responde ÚNICAMENTE basándote en este contexto de MongoDB:\n{contexto_bd}\n\nPregunta: {pregunta}"
            respuesta = ollama.chat(model="llama3.2:1b", messages=[{"role": "user", "content": prompt}])
            texto_respuesta = respuesta["message"]["content"]
        except Exception as e:
            texto_respuesta = f"Error IA: {e}"

        ventana.after(0, mostrar_respuesta_rag, texto_respuesta)
    threading.Thread(target=tarea_rag, daemon=True).start()

def mostrar_respuesta_rag(respuesta):
    chat_rag.config(state=tk.NORMAL)
    chat_rag.insert(tk.END, f"LogiSmart AI: ", "ai_name")
    chat_rag.insert(tk.END, f"{respuesta}\n\n", "ai")
    chat_rag.config(state=tk.DISABLED)
    chat_rag.see(tk.END)
    btn_enviar_rag.config(state=tk.NORMAL, text="Enviar Consulta")
    entry_rag.config(state=tk.NORMAL)
    entry_rag.focus()

def actualizar_tabla_historial():
    for item in tabla_historial.get_children(): tabla_historial.delete(item)
    try:
        if incidentes_col is not None:
            for reg in incidentes_col.find().sort("fecha_reporte", -1).limit(50):
                fecha = reg.get("fecha_reporte", "")
                fecha_str = fecha[:16] if isinstance(fecha, str) else fecha.strftime("%Y-%m-%d %H:%M") 
                clasif = reg.get("clasificacion", "N/A")
                prio = reg.get("prioridad", "N/A")
                datos = reg.get("datos_extraidos", {})
                tabla_historial.insert("", tk.END, values=(fecha_str, clasif, prio, datos.get("placa", "N/A"), datos.get("ubicacion", "N/A")))
    except Exception as e:
        messagebox.showerror("Error", f"Fallo al cargar historial: {e}")

def exportar_historial_csv():
    if len(tabla_historial.get_children()) == 0:
        messagebox.showwarning("Sin datos", "No hay incidentes para exportar.")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("Archivos CSV", "*.csv")], title="Guardar Reporte")
    if not filepath: return
    try:
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(columnas_hist)
            for row_id in tabla_historial.get_children():
                writer.writerow(tabla_historial.item(row_id)['values'])
        messagebox.showinfo("Éxito", f"Reporte exportado a:\n{filepath}")
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo exportar: {e}")

def navegar_a(index): notebook.select(index)

# ==========================================
# CONFIGURACIÓN VISUAL Y VENTANA
# ==========================================
ventana = tk.Tk()
ventana.title("LogiSmart - Centro de Control Inteligente")
try: ventana.attributes('-zoomed', True)
except: ventana.state('zoomed')
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

# === PESTAÑA 0: INICIO ===
frame_inicio = tk.Frame(notebook, bg="#FFFFFF")
notebook.add(frame_inicio, text="Inicio")
container_inicio = tk.Frame(frame_inicio, bg="#FFFFFF", padx=40, pady=40)
container_inicio.pack(expand=True, fill="both")
tk.Label(container_inicio, text="Bienvenido a LogiSmart", font=("Segoe UI", 24, "bold"), bg="#FFFFFF", fg="#1E293B").pack(anchor="w", pady=(0, 10))
tk.Label(container_inicio, text="Centro de Control Inteligente para gestión logística impulsado por Llama 3.2.", font=("Segoe UI", 12), bg="#FFFFFF", fg="#64748B").pack(anchor="w", pady=(0, 30))

frame_cards = tk.Frame(container_inicio, bg="#FFFFFF")
frame_cards.pack(fill="both", expand=True)
secciones = [
    ("Control de Accesos", "Evalúa requisitos de ingreso con simulador lógico en vivo.", 1),
    ("Análisis de Incidentes (IA)", "Extrae datos estructurados desde reportes de texto libre.", 2),
    ("Asistente RAG", "Realiza consultas en lenguaje natural a la base de datos.", 3),
    ("Matriz Ética", "Gestión de riesgos éticos y gráfica de impacto residual.", 4),
    ("Historial MongoDB", "Bandeja dinámica de incidentes con exportación a CSV.", 5)
]
for i, (titulo, desc, index) in enumerate(secciones):
    card = tk.Frame(frame_cards, bg="#F8FAFC", padx=20, pady=20, highlightbackground="#E2E8F0", highlightthickness=1)
    card.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
    frame_cards.grid_columnconfigure(i%2, weight=1)
    tk.Label(card, text=titulo, font=("Segoe UI", 14, "bold"), bg="#F8FAFC", fg="#2563EB").pack(anchor="w")
    tk.Label(card, text=desc, font=("Segoe UI", 10), bg="#F8FAFC", fg="#475569").pack(anchor="w", pady=(5, 15))
    tk.Button(card, text="Ir a la sección", command=lambda idx=index: navegar_a(idx), font=("Segoe UI", 10, "bold"), bg="#E2E8F0", fg="#1E293B", relief=tk.FLAT).pack(anchor="w")

# === PESTAÑA 1: CONTROL DE ACCESOS ===
frame_accesos = tk.Frame(notebook, bg="#F4F6F9")
notebook.add(frame_accesos, text="Control de Accesos")
paned_accesos = tk.PanedWindow(frame_accesos, orient=tk.HORIZONTAL, bg="#E2E8F0", sashwidth=5)
paned_accesos.pack(fill="both", expand=True)

frame_form = tk.Frame(paned_accesos, bg="#FFFFFF", padx=20, pady=20)
paned_accesos.add(frame_form, minsize=400)
tk.Label(frame_form, text="Formulario de Ingreso y Simulación Lógica", font=FONT_TITLE, bg="#FFFFFF", fg="#1E293B").pack(anchor="w", pady=(0,5))
tk.Label(frame_form, text="Ingresa los datos y marca las casillas. El sistema evaluará el acceso en tiempo real basándose en las premisas lógicas P, Q, R, S, T, U.", font=("Segoe UI", 10), bg="#FFFFFF", fg="#64748B", wraplength=350, justify="left").pack(anchor="w", pady=(0, 15))

tk.Label(frame_form, text="Placa del Vehículo:", font=FONT_NORM, bg="#FFFFFF").pack(anchor="w")
entry_placa = tk.Entry(frame_form, font=FONT_NORM, width=30, bg="#F8FAFC", relief=tk.SOLID)
entry_placa.pack(pady=(0,10), ipady=4, anchor="w")
tk.Label(frame_form, text="Operador en turno:", font=FONT_NORM, bg="#FFFFFF").pack(anchor="w")
entry_operador = tk.Entry(frame_form, font=FONT_NORM, width=30, bg="#F8FAFC", relief=tk.SOLID)
entry_operador.pack(pady=(0,20), ipady=4, anchor="w")

var_P, var_Q, var_R = tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()
var_S, var_T, var_U = tk.BooleanVar(), tk.BooleanVar(), tk.BooleanVar()
for texto, variable in [("(P) Autorización Previa", var_P), ("(S) Certificación Conductor", var_S), ("(T) Horario Permitido", var_T), ("(U) Seguro Vigente", var_U), ("(Q) Exceso de Peso", var_Q), ("(R) Material Peligroso", var_R)]:
    tk.Checkbutton(frame_form, text=texto, variable=variable, font=FONT_NORM, bg="#FFFFFF", activebackground="#FFFFFF", command=evaluar_acceso).pack(anchor="w", pady=2)

frame_res = tk.Frame(paned_accesos, bg="#F8FAFC", padx=20, pady=20)
paned_accesos.add(frame_res, minsize=400)
tk.Label(frame_res, text="Estado de Acceso (Semáforo)", font=FONT_TITLE, bg="#F8FAFC").pack(anchor="w")
lbl_semaforo = tk.Label(frame_res, text="ESPERANDO VEHÍCULO...", font=("Segoe UI", 16, "bold"), bg="#94A3B8", fg="white", pady=15)
lbl_semaforo.pack(fill="x", pady=10)
tk.Label(frame_res, text="Justificación del Sistema (Trazabilidad):", font=FONT_TITLE, bg="#F8FAFC").pack(anchor="w", pady=(10,0))
texto_explicacion = tk.Text(frame_res, bg="#FFFFFF", fg="#334155", font=("Consolas", 11), relief=tk.SOLID, padx=10, pady=10)
texto_explicacion.pack(fill="both", expand=True)

# === PESTAÑA 2: INCIDENTES IA ===
frame_ia = tk.Frame(notebook, bg="#F4F6F9")
notebook.add(frame_ia, text="Análisis de Incidentes (IA)")
paned_ia = tk.PanedWindow(frame_ia, orient=tk.HORIZONTAL, bg="#E2E8F0", sashwidth=5)
paned_ia.pack(fill="both", expand=True)

frame_ia_in = tk.Frame(paned_ia, bg="#FFFFFF", padx=20, pady=20)
paned_ia.add(frame_ia_in, minsize=400)
tk.Label(frame_ia_in, text="Bandeja de Entrada del Operador", font=FONT_TITLE, bg="#FFFFFF", fg="#1E293B").pack(anchor="w", pady=(0, 5))
tk.Label(frame_ia_in, text="Pega aquí el correo o reporte enviado por el personal logístico. La IA leerá el texto, extraerá los datos clave y los estructurará automáticamente.", font=("Segoe UI", 10), bg="#FFFFFF", fg="#64748B", wraplength=350, justify="left").pack(anchor="w", pady=(0, 10))
tk.Button(frame_ia_in, text="Cargar Reporte de Ejemplo", command=cargar_ejemplo_correo, bg="#E2E8F0").pack(anchor="w", pady=5)
text_correo = tk.Text(frame_ia_in, bg="#F8FAFC", font=FONT_NORM, relief=tk.SOLID)
text_correo.pack(fill="both", expand=True)
btn_clasificar = tk.Button(frame_ia_in, text="Procesar Incidente con IA", command=clasificar_correo, bg="#4F46E5", fg="white", font=FONT_TITLE)
btn_clasificar.pack(fill="x", pady=10, ipady=5)

frame_ia_out = tk.Frame(paned_ia, bg="#F8FAFC", padx=20, pady=20)
paned_ia.add(frame_ia_out, minsize=400)
tk.Label(frame_ia_out, text="Extracción Inteligente de Datos", font=FONT_TITLE, bg="#F8FAFC", fg="#1E293B").pack(anchor="w", pady=(0, 5))
lbl_ai_estado = tk.Label(frame_ia_out, text="Esperando reporte...", font=("Segoe UI", 10, "italic"), bg="#F8FAFC", fg="#64748B")
lbl_ai_estado.pack(anchor="w", pady=(0, 15))

frame_grid = tk.Frame(frame_ia_out, bg="#F8FAFC")
frame_grid.pack(fill="x")
tk.Label(frame_grid, text="Categoría:", font=FONT_NORM, bg="#F8FAFC", fg="#64748B").grid(row=0, column=0, sticky="w", pady=5, padx=(0,10))
lbl_ai_clasificacion = tk.Label(frame_grid, text="--", font=("Segoe UI", 12, "bold"), bg="#F8FAFC", fg="#0F172A")
lbl_ai_clasificacion.grid(row=0, column=1, sticky="w", pady=5)
tk.Label(frame_grid, text="Prioridad:", font=FONT_NORM, bg="#F8FAFC", fg="#64748B").grid(row=1, column=0, sticky="w", pady=5, padx=(0,10))
lbl_ai_prioridad = tk.Label(frame_grid, text="--", font=("Segoe UI", 12, "bold"), bg="#F8FAFC")
lbl_ai_prioridad.grid(row=1, column=1, sticky="w", pady=5)
tk.Label(frame_grid, text="Placa:", font=FONT_NORM, bg="#F8FAFC", fg="#64748B").grid(row=2, column=0, sticky="w", pady=5, padx=(0,10))
lbl_ai_placa = tk.Label(frame_grid, text="--", font=FONT_TITLE, bg="#F8FAFC", fg="#0F172A")
lbl_ai_placa.grid(row=2, column=1, sticky="w", pady=5)
tk.Label(frame_grid, text="Ubicación:", font=FONT_NORM, bg="#F8FAFC", fg="#64748B").grid(row=3, column=0, sticky="w", pady=5, padx=(0,10))
lbl_ai_ubicacion = tk.Label(frame_grid, text="--", font=FONT_TITLE, bg="#F8FAFC", fg="#0F172A")
lbl_ai_ubicacion.grid(row=3, column=1, sticky="w", pady=5)

tk.Label(frame_ia_out, text="Estructura JSON (Para MongoDB):", font=("Segoe UI", 10, "bold"), bg="#F8FAFC", fg="#64748B").pack(anchor="w", pady=(20, 5))
text_json_crudo = tk.Text(frame_ia_out, height=10, bg="#1E293B", fg="#A7F3D0", font=("Consolas", 10))
text_json_crudo.pack(fill="both", expand=True)

# === PESTAÑA 3: RAG ===
frame_rag_tab = tk.Frame(notebook, bg="#FFFFFF", padx=20, pady=20)
notebook.add(frame_rag_tab, text="Asistente RAG")
tk.Label(frame_rag_tab, text="Consulta a la Base de Datos con Lenguaje Natural", font=FONT_TITLE, bg="#FFFFFF", fg="#1E293B").pack(anchor="w", pady=(0, 5))
tk.Label(frame_rag_tab, text="Haz preguntas al asistente. La IA revisará el historial de MongoDB (últimos accesos e incidentes) para darte una respuesta certera.", font=("Segoe UI", 10), bg="#FFFFFF", fg="#64748B").pack(anchor="w", pady=(0, 15))

chat_rag = scrolledtext.ScrolledText(frame_rag_tab, font=FONT_NORM, bg="#F8FAFC", relief=tk.SOLID)
chat_rag.pack(fill="both", expand=True, pady=10)
chat_rag.tag_config("user_name", foreground="#2563EB", font=("Segoe UI", 11, "bold"))
chat_rag.tag_config("ai_name", foreground="#059669", font=("Segoe UI", 11, "bold"))
frame_rag_input = tk.Frame(frame_rag_tab, bg="#FFFFFF")
frame_rag_input.pack(fill="x")
entry_rag = tk.Entry(frame_rag_input, font=FONT_NORM, bg="#F8FAFC", relief=tk.SOLID)
entry_rag.pack(side=tk.LEFT, fill="x", expand=True, ipady=6)
entry_rag.bind("<Return>", enviar_pregunta_rag)
btn_enviar_rag = tk.Button(frame_rag_input, text="Enviar Consulta", command=enviar_pregunta_rag, bg="#2563EB", fg="white")
btn_enviar_rag.pack(side=tk.RIGHT, ipady=4, ipadx=10, padx=5)

# === PESTAÑA 4: MATRIZ DE RIESGOS ===
frame_etica = tk.Frame(notebook, bg="#FFFFFF", padx=20, pady=20)
notebook.add(frame_etica, text="Matriz de Riesgos")

paned_etica = tk.PanedWindow(frame_etica, orient=tk.HORIZONTAL, bg="#E2E8F0", sashwidth=5)
paned_etica.pack(fill="both", expand=True)

frame_crud_etica = tk.Frame(paned_etica, bg="#FFFFFF")
paned_etica.add(frame_crud_etica, minsize=500)

tk.Label(frame_crud_etica, text="Gestión de Riesgos Éticos (IA)", font=FONT_TITLE, bg="#FFFFFF").pack(anchor="w", pady=(0,5))
tk.Label(frame_crud_etica, text="Tabla de riesgos y estrategias de mitigación implementadas en el sistema.", font=("Segoe UI", 10), bg="#FFFFFF", fg="#64748B").pack(anchor="w", pady=(0, 10))

columnas_etica = ("Riesgo", "Categoría", "Puntaje Inicial", "Puntaje Residual", "Mitigación")
tabla_riesgos = ttk.Treeview(frame_crud_etica, columns=columnas_etica, show="headings", height=6)
tabla_riesgos.column("Riesgo", width=180)
tabla_riesgos.column("Categoría", width=80)
tabla_riesgos.column("Puntaje Inicial", width=100, anchor="center")
tabla_riesgos.column("Puntaje Residual", width=100, anchor="center")
tabla_riesgos.column("Mitigación", width=200)
for col in columnas_etica: tabla_riesgos.heading(col, text=col)
tabla_riesgos.pack(fill="x", pady=5)

datos_base_etica = [
    ("Alucinaciones del LLM en clasificación", "Técnico", 9, 3, "Clasificador estático de respaldo (Híbrido)."),
    ("Sesgo en correos con ortografía informal", "Ético", 7, 2, "Auditoría humana en prioridades Altas."),
    ("Privacidad de datos del conductor", "Legal", 10, 4, "Ejecución de Ollama 100% en local (sin internet)."),
    ("Dependencia excesiva automatización", "Operativo", 8, 3, "El operador toma decisión final con semáforo.")
]
for d in datos_base_etica: tabla_riesgos.insert("", tk.END, values=d)

frame_grafica = tk.Frame(paned_etica, bg="#F8FAFC")
paned_etica.add(frame_grafica, minsize=400)

figura, ax = plt.subplots(figsize=(5, 4), dpi=100)
canvas_grafica = FigureCanvasTkAgg(figura, frame_grafica)
canvas_grafica.get_tk_widget().pack(fill="both", expand=True, pady=10)

def actualizar_grafica_riesgos():
    nombres, iniciales, residuales = [], [], []
    for item in tabla_riesgos.get_children():
        valores = tabla_riesgos.item(item)['values']
        nombres.append(str(valores[0])[:15] + "..")
        iniciales.append(int(valores[2]))
        residuales.append(int(valores[3]))
        
    ax.clear()
    x = range(len(nombres))
    ancho = 0.35
    
    ax.bar([i - ancho/2 for i in x], iniciales, ancho, label='Riesgo Inicial', color='#EF4444')
    ax.bar([i + ancho/2 for i in x], residuales, ancho, label='Riesgo Residual', color='#10B981')
    
    ax.set_ylabel('Nivel de Impacto (1-10)')
    ax.set_title('Matriz de Mitigación de Riesgos')
    ax.set_xticks(x)
    ax.set_xticklabels(nombres, rotation=15, ha="right", fontsize=8)
    ax.legend()
    figura.tight_layout()
    canvas_grafica.draw()

def eliminar_riesgo():
    seleccion = tabla_riesgos.selection()
    if not seleccion:
        messagebox.showwarning("Atención", "Selecciona un riesgo de la tabla para eliminar.")
        return
    for item in seleccion: tabla_riesgos.delete(item)
    actualizar_grafica_riesgos()

tk.Button(frame_crud_etica, text="Eliminar Riesgo Seleccionado", command=eliminar_riesgo, bg="#EF4444", fg="white").pack(anchor="e", pady=5)
actualizar_grafica_riesgos()


# === PESTAÑA 5: HISTORIAL ===
frame_historial = tk.Frame(notebook, bg="#FFFFFF", padx=20, pady=20)
notebook.add(frame_historial, text="Historial de Incidentes")
tk.Label(frame_historial, text="Bandeja Histórica de Incidentes", font=FONT_TITLE, bg="#FFFFFF", fg="#1E293B").pack(anchor="w", pady=(0, 5))
tk.Label(frame_historial, text="Visualización en tiempo real de los reportes almacenados en MongoDB Atlas.", font=("Segoe UI", 10), bg="#FFFFFF", fg="#64748B").pack(anchor="w", pady=(0, 10))

frame_controles_hist = tk.Frame(frame_historial, bg="#FFFFFF")
frame_controles_hist.pack(fill="x", pady=10)
columnas_hist = ("Fecha del Reporte", "Clasificación", "Prioridad", "Placa", "Ubicación")
tabla_historial = ttk.Treeview(frame_historial, columns=columnas_hist, show="headings", height=15)
for col in columnas_hist: tabla_historial.heading(col, text=col)
tabla_historial.pack(fill="both", expand=True)

tk.Button(frame_controles_hist, text="Refrescar Tabla", command=actualizar_tabla_historial, bg="#10B981", fg="white").pack(side=tk.RIGHT, padx=5)
tk.Button(frame_controles_hist, text="Exportar a CSV", command=exportar_historial_csv, bg="#F59E0B", fg="white").pack(side=tk.RIGHT, padx=5)
actualizar_tabla_historial()

ventana.mainloop()