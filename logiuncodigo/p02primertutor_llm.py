import tkinter as tk
from tkinter import scrolledtext
import threading
import ollama

# ============================================================
# CONFIGURACIÓN DEL MODELO Y SISTEMA
# ============================================================
MODELO = "llama3.2:1b"

mensaje_sistema = """
Eres un profesor experto en Git, GitHub y control de versiones.
Tu función es ayudar a estudiantes universitarios de ingeniería de software.

El estudiante con el que hablas es Osvaldo, estudiante de Desarrollo de Software Multiplataforma en la UTVT. A sus 20 años tiene experiencia desarrollando en React, Node.js, PHP y bases de datos. Ha trabajado en proyectos del equipo JOZ Team como LunaVet, ParcePet y LumaIA.

Debes:
1. Explicar comandos de Git de manera clara y directa.
2. Utilizar ejemplos relacionados con el stack web y móvil (React, Node.js).
3. Explicar cómo solucionar conflictos de merge, hacer rebase o gestionar ramas.
4. Si Osvaldo pregunta sobre buenas prácticas, relaciónalas con el trabajo en equipo (ej. JOZ Team).
5. No proporcionar únicamente la respuesta final; explica el concepto brevemente.
"""

mensajes = [{"role": "system", "content": mensaje_sistema}]

# ============================================================
# FUNCIONES DE LA INTERFAZ
# ============================================================
def enviar_mensaje(event=None):
    """Captura el texto, lo muestra y llama al LLM en un hilo separado."""
    pregunta = entrada_texto.get("1.0", tk.END).strip()
    if not pregunta:
        return "break" # Evitar saltos de línea vacíos
    
    # Mostrar mensaje de Osvaldo
    mostrar_en_chat("Osvaldo", pregunta, "user")
    entrada_texto.delete("1.0", tk.END)
    mensajes.append({"role": "user", "content": pregunta})
    
    # Bloquear entrada mientras el LLM piensa
    entrada_texto.config(state=tk.DISABLED)
    btn_enviar.config(state=tk.DISABLED)
    ventana.title("Tutor Inteligente de GitHub - Pensando...")
    
    # Iniciar hilo para no congelar la ventana gráfica
    threading.Thread(target=obtener_respuesta_llm, daemon=True).start()
    return "break"

def obtener_respuesta_llm():
    """Se comunica con Ollama en segundo plano."""
    try:
        respuesta = ollama.chat(model=MODELO, messages=mensajes)
        contenido = respuesta["message"]["content"]
        mensajes.append({"role": "assistant", "content": contenido})
        
        # Enviar respuesta a la ventana principal de forma segura
        ventana.after(0, mostrar_en_chat, "Tutor", contenido, "assistant")
    except Exception as e:
        error_msg = f"Error al conectar con Ollama: {str(e)}\n¿Está el servicio activo (sudo systemctl start ollama)?"
        mensajes.pop() # Quitar la pregunta fallida del historial
        ventana.after(0, mostrar_en_chat, "Sistema", error_msg, "error")
    finally:
        ventana.after(0, reactivar_interfaz)

def reactivar_interfaz():
    """Vuelve a habilitar la caja de texto tras recibir respuesta."""
    entrada_texto.config(state=tk.NORMAL)
    btn_enviar.config(state=tk.NORMAL)
    ventana.title("Tutor Inteligente de GitHub")
    entrada_texto.focus()

def mostrar_en_chat(remitente, mensaje, tag):
    """Inserta el texto en el área de chat con sus colores respectivos."""
    chat_historial.config(state=tk.NORMAL)
    chat_historial.insert(tk.END, f"{remitente}:\n", f"{tag}_name")
    chat_historial.insert(tk.END, f"{mensaje}\n\n", tag)
    chat_historial.config(state=tk.DISABLED)
    chat_historial.see(tk.END) # Hacer autoscroll hacia abajo

# ============================================================
# CONSTRUCCIÓN DE LA VENTANA (TKINTER)
# ============================================================
ventana = tk.Tk()
ventana.title("Tutor Inteligente de GitHub")
ventana.geometry("750x600")
ventana.configure(bg="#1e1e1e")

# Área de historial de chat
chat_historial = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, font=("Segoe UI", 11), bg="#2d2d2d", fg="#ffffff", padx=15, pady=15, borderwidth=0)
chat_historial.pack(padx=10, pady=(10, 5), fill=tk.BOTH, expand=True)

# Configuración de colores (Tags)
chat_historial.tag_config("user_name", foreground="#4da6ff", font=("Segoe UI", 11, "bold"))
chat_historial.tag_config("user", foreground="#ffffff")
chat_historial.tag_config("assistant_name", foreground="#33cc33", font=("Segoe UI", 11, "bold"))
chat_historial.tag_config("assistant", foreground="#d9d9d9")
chat_historial.tag_config("error_name", foreground="#ff3333", font=("Segoe UI", 11, "bold"))
chat_historial.tag_config("error", foreground="#ff9999")
chat_historial.config(state=tk.DISABLED)

# Contenedor inferior (Input + Botón)
frame_inferior = tk.Frame(ventana, bg="#1e1e1e")
frame_inferior.pack(padx=10, pady=(5, 10), fill=tk.X)

entrada_texto = tk.Text(frame_inferior, height=3, font=("Segoe UI", 11), bg="#3d3d3d", fg="#ffffff", insertbackground="white", borderwidth=0, padx=10, pady=10)
entrada_texto.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
# Enviar con Enter (Shift+Enter para salto de línea)
entrada_texto.bind("<Return>", lambda e: enviar_mensaje() if not e.state & 0x0001 else None)

btn_enviar = tk.Button(frame_inferior, text="Enviar", font=("Segoe UI", 11, "bold"), bg="#007acc", fg="white", command=enviar_mensaje, relief=tk.FLAT, padx=20, cursor="hand2")
btn_enviar.pack(side=tk.RIGHT, fill=tk.Y)

# Mensaje de bienvenida inicial
bienvenida = (
    "--- RESUMEN DE TU PERFIL CARGADO ---\n"
    "Usuario: Osvaldo Salinas Aranda (20 años)\n"
    "Formación: Ing. en Desarrollo de Software Multiplataforma (UTVT)\n"
    "Proyectos destacados: LunaVet, LumaIA, ParcePet (JOZ Team).\n"
    "------------------------------------\n\n"
    "¡Hola Osvaldo! Soy tu tutor experto en Git y GitHub. Puedes escribir tu pregunta abajo o presionar 'Enter' para enviarla. ¿En qué te puedo ayudar hoy?"
)
mostrar_en_chat("Sistema", bienvenida, "assistant")

# Iniciar aplicación
entrada_texto.focus()
ventana.mainloop()