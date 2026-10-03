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
    pregunta = entrada_texto.get().strip()
    if not pregunta:
        return "break"
    
    mostrar_en_chat("<Osvaldo>", pregunta, "user")
    entrada_texto.delete(0, tk.END)
    mensajes.append({"role": "user", "content": pregunta})
    
    entrada_texto.config(state=tk.DISABLED)
    btn_enviar.config(state=tk.DISABLED)
    ventana.title("Minecraft - Generando terreno (Pensando)...")
    
    threading.Thread(target=obtener_respuesta_llm, daemon=True).start()
    return "break"

def obtener_respuesta_llm():
    try:
        respuesta = ollama.chat(model=MODELO, messages=mensajes)
        contenido = respuesta["message"]["content"]
        mensajes.append({"role": "assistant", "content": contenido})
        
        ventana.after(0, mostrar_en_chat, "<Tutor_GitHub>", contenido, "assistant")
    except Exception as e:
        error_msg = f"Error de conexión: {str(e)}"
        mensajes.pop()
        ventana.after(0, mostrar_en_chat, "<Sistema>", error_msg, "error")
    finally:
        ventana.after(0, reactivar_interfaz)

def reactivar_interfaz():
    entrada_texto.config(state=tk.NORMAL)
    btn_enviar.config(state=tk.NORMAL)
    ventana.title("Tutor Inteligente de GitHub - Edición Bloques")
    entrada_texto.focus()

def mostrar_en_chat(remitente, mensaje, tag):
    chat_historial.config(state=tk.NORMAL)
    chat_historial.insert(tk.END, f"{remitente} ", f"{tag}_name")
    chat_historial.insert(tk.END, f"{mensaje}\n\n", tag)
    chat_historial.config(state=tk.DISABLED)
    chat_historial.see(tk.END)

# ============================================================
# CONSTRUCCIÓN DE LA VENTANA (ESTÉTICA MINECRAFT)
# ============================================================
ventana = tk.Tk()
ventana.title("Tutor Inteligente de GitHub - Edición Bloques")
ventana.geometry("800x600")
# Fondo gris que simula piedra (Stone)
ventana.configure(bg="#7B7B7B", padx=15, pady=15)

# Fuente retro para simular píxeles
MC_FONT = ("Courier New", 12, "bold")

# Área de historial de chat (Fondo oscuro semitransparente clásico del juego)
chat_historial = scrolledtext.ScrolledText(
    ventana, 
    wrap=tk.WORD, 
    font=MC_FONT, 
    bg="#1E1E1E", 
    fg="#FFFFFF", 
    padx=15, 
    pady=15, 
    borderwidth=4, 
    relief=tk.SUNKEN
)
chat_historial.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

# Colores inspirados en el chat de Minecraft
chat_historial.tag_config("user_name", foreground="#FFFF55") # Amarillo MC
chat_historial.tag_config("user", foreground="#FFFFFF")
chat_historial.tag_config("assistant_name", foreground="#55FF55") # Verde claro MC
chat_historial.tag_config("assistant", foreground="#D9D9D9")
chat_historial.tag_config("error_name", foreground="#FF5555") # Rojo MC
chat_historial.tag_config("error", foreground="#FF5555")
chat_historial.config(state=tk.DISABLED)

# Contenedor inferior
frame_inferior = tk.Frame(ventana, bg="#7B7B7B")
frame_inferior.pack(fill=tk.X)

# Label decorativo del input (El clásico ">" del chat)
lbl_cursor = tk.Label(frame_inferior, text=">", font=MC_FONT, bg="#7B7B7B", fg="#FFFFFF")
lbl_cursor.pack(side=tk.LEFT, padx=(0, 5))

# Input de texto con borde hundido
entrada_texto = tk.Entry(
    frame_inferior, 
    font=MC_FONT, 
    bg="#3C3C3C", 
    fg="#FFFFFF", 
    insertbackground="white", 
    borderwidth=3, 
    relief=tk.SUNKEN
)
entrada_texto.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15), ipady=5)
entrada_texto.bind("<Return>", enviar_mensaje)

# Botón estilo bloque (Gris con borde en relieve grueso)
btn_enviar = tk.Button(
    frame_inferior, 
    text="Craftear", 
    font=MC_FONT, 
    bg="#8B8B8B", 
    activebackground="#A0A0A0",
    fg="#000000", 
    command=enviar_mensaje, 
    borderwidth=5, 
    relief=tk.RAISED,
    cursor="hand2"
)
btn_enviar.pack(side=tk.RIGHT, ipadx=10)

# Mensaje de bienvenida inicial
bienvenida = (
    "¡Jugador Osvaldo se unió a la partida!\n"
    "Sistema cargado con experiencia en UTVT y JOZ Team.\n\n"
    "Escribe tu duda sobre Git en la barra inferior para comenzar."
)
mostrar_en_chat("<Server>", bienvenida, "assistant")

entrada_texto.focus()
ventana.mainloop()