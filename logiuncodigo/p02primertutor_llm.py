# ============================================================
# PRACTICA 2
# TUTOR INTELIGENTE DE GITHUB CON LLM
# ============================================================
#
# Objetivo:
# Crear un asistente educativo especializado en control de 
# versiones (Git/GitHub) utilizando Ollama.
#
# Modelo:
# llama3.2
# ============================================================

import ollama

MODELO = "llama3.2"

# ------------------------------------------------------------
# CONFIGURACIÓN DEL SISTEMA Y CONTEXTO DEL USUARIO
# ------------------------------------------------------------
mensaje_sistema = """
Eres un profesor experto en Git, GitHub y control de versiones.
Tu función es ayudar a estudiantes universitarios de ingeniería de software.

El estudiante con el que hablas es Osvaldo, estudiante de Desarrollo de Software 
Multiplataforma en la UTVT, a sus 20 años tiene experiencia desarrollando en React, 
Node.js, PHP y bases de datos. Ha trabajado en proyectos del equipo JOZ Team como 
LunaVet, ParcePet y LumaIA.

Debes:
1. Explicar comandos de Git y flujos de trabajo de GitHub de manera clara.
2. Utilizar ejemplos relacionados con el stack web y móvil (React, Node.js).
3. Explicar cómo solucionar conflictos de merge, hacer rebase o gestionar ramas.
4. Si Osvaldo pregunta sobre buenas prácticas, relaciónalas con el trabajo en equipo (ej. JOZ Team).
5. No proporcionar únicamente la respuesta final; explica el concepto detrás del comando.
"""

mensajes = [
    {
        "role": "system",
        "content": mensaje_sistema
    }
]

# ------------------------------------------------------------
# ENCABEZADO Y RESUMEN DEL HISTORIAL (REQUERIMIENTO 3)
# ------------------------------------------------------------
print("=" * 60)
print("          TUTOR INTELIGENTE DE GITHUB Y GIT")
print("=" * 60)
print(f"Modelo utilizado: {MODELO}\n")

# Resumen del historial mostrado al usuario
print("--- RESUMEN DE TU PERFIL CARGADO ---")
print("Usuario: Osvaldo Salinas Aranda (20 años)")
print("Formación: Ingeniería en Desarrollo de Software Multiplataforma (UTVT)")
print("Tecnologías clave: React, React Native, Node.js, PHP, TypeScript, Docker.")
print("Proyectos destacados: LunaVet, LumaIA, ParcePet (JOZ Team).")
print("------------------------------------\n")

print("Escribe 'salir' para terminar.\n")

# ------------------------------------------------------------
# BUCLE PRINCIPAL
# ------------------------------------------------------------
while True:
    pregunta = input("Osvaldo: ")

    if pregunta.lower() == "salir":
        print("\nSesión finalizada. ¡Éxito en tus commits!")
        break

    mensajes.append({"role": "user", "content": pregunta})

    try:
        # Añadir un indicador visual de carga
        print("Tutor pensando...", end="\r")
        
        respuesta = ollama.chat(
            model=MODELO,
            messages=mensajes
        )

    except Exception as error:
        print("\nERROR AL CONECTARSE CON EL LLM")
        print("--------------------------------")
        print(error)
        print("\nVerifica que el servicio de Ollama esté ejecutándose en Ubuntu (sudo systemctl status ollama).")
        mensajes.pop()
        continue

    contenido = respuesta["message"]["content"]
    mensajes.append({"role": "assistant", "content": contenido})

    # Limpiar la línea de carga y mostrar la respuesta
    print(" " * 20, end="\r") 
    print("TUTOR:")
    print(contenido)
    print("-" * 60)