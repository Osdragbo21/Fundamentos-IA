import tkinter as tk
from tkinter import ttk

# 1. Definimos los estados
A = {'B', 'C'}
B = {'A', 'D'}
C = {'A', 'E'}
D = {'B'}
E = {'C', 'F'}
F = {'E'}

grafo = {'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F}

# 2. Función para buscar rutas detectando finales dinámicamente
def buscar_recorridos(nodo, ruta_actual, lista_resultados):
    ruta = ruta_actual + [nodo]
    
    # Encontramos los vecinos a los que podemos ir (que no estén ya en la ruta)
    vecinos_posibles = [n for n in grafo[nodo] if n not in ruta]
    
    # Si ya no hay vecinos nuevos a los que ir, terminamos esta ruta
    if not vecinos_posibles:
        lista_resultados.append("-".join(ruta).lower())
        return
        
    for destino in vecinos_posibles:
        buscar_recorridos(destino, ruta, lista_resultados)

# 3. Función que actualiza los textos y el diagrama en la interfaz
def calcular_y_dibujar(*args):
    estado_inicial = combo_inicio.get()
    
    # Calcular rutas
    resultados = []
    buscar_recorridos(estado_inicial, [], resultados)
    
    # Mostrar texto
    caja_texto.delete(1.0, tk.END)
    caja_texto.insert(tk.END, f"Rutas desde '{estado_inicial}':\n\n")
    for ruta in resultados:
        caja_texto.insert(tk.END, f"  {ruta}\n")
        
    # Dibujar el diagrama
    dibujar_grafo(estado_inicial)

# 4. Función para dibujar el árbol usando Tkinter Canvas
def dibujar_grafo(estado_inicial):
    canvas.delete("all") # Limpiamos el dibujo anterior
    
    # Coordenadas (x, y) de cada nodo para darle forma de árbol
    coords = {
        'A': (150, 30),
        'B': (70, 100),
        'C': (230, 100),
        'D': (70, 170),
        'E': (230, 170),
        'F': (230, 240)
    }
    
    # Primero dibujamos las líneas (aristas) para que queden debajo
    dibujadas = set()
    for nodo, vecinos in grafo.items():
        for vec in vecinos:
            # Ordenamos para no dibujar la línea A-B y luego B-A
            arista = tuple(sorted([nodo, vec]))
            if arista not in dibujadas:
                x1, y1 = coords[nodo]
                x2, y2 = coords[vec]
                canvas.create_line(x1, y1, x2, y2, fill="#7f8c8d", width=2)
                dibujadas.add(arista)
                
    # Luego dibujamos los círculos (nodos) encima
    for nodo, (x, y) in coords.items():
        # Color del nodo: Verde si es el inicial, Gris azulado para el resto
        if nodo == estado_inicial:
            color_fondo = "#2ecc71" # Verde
            color_texto = "white"
        else:
            color_fondo = "#ecf0f1" # Gris muy claro
            color_texto = "black"
            
        canvas.create_oval(x-18, y-18, x+18, y+18, fill=color_fondo, outline="#34495e", width=2)
        canvas.create_text(x, y, text=nodo, font=("Arial", 11, "bold"), fill=color_texto)

# 5. Configuración de la interfaz visual
ventana = tk.Tk()
ventana.title("Árbol de Decisiones Interactivo")
ventana.geometry("350x550")
ventana.configure(padx=20, pady=20, bg="white")

# Controles Superiores
frame_top = tk.Frame(ventana, bg="white")
frame_top.pack(fill="x", pady=(0, 10))

tk.Label(frame_top, text="Estado inicial:", bg="white", font=("Arial", 10, "bold")).pack(side="left")

# Menú desplegable (Combobox)
opciones = ['A', 'B', 'C', 'D', 'E', 'F']
combo_inicio = ttk.Combobox(frame_top, values=opciones, state="readonly", width=5)
combo_inicio.set('A') # Valor por defecto
combo_inicio.pack(side="left", padx=10)

# Cuando se cambie la opción en el selector, recalculamos automáticamente
combo_inicio.bind("<<ComboboxSelected>>", calcular_y_dibujar)

# Caja de resultados
caja_texto = tk.Text(ventana, height=5, width=35, font=("Consolas", 11), bg="#f8f9fa", relief="solid")
caja_texto.pack(pady=10)

# Lienzo para el diagrama
tk.Label(ventana, text="Diagrama de la red:", bg="white", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
canvas = tk.Canvas(ventana, width=300, height=300, bg="white", highlightthickness=0)
canvas.pack()

# Dibujar la primera vez para el nodo 'A'
calcular_y_dibujar()

ventana.mainloop()