
estados = {'A', 'B', 'C', 'D', 'E', 'F'}

A = {'B', 'C'}
B = {'A', 'D'}
C = {'A', 'E'}
D = {'B'}
E = {'C', 'F'}
F = {'E'}

# a-c-e-f y a-b-d, estado inicial a
#Rutas posibles

grafo = {'A': A, 'B': B, 'C': C, 'D': D, 'E': E, 'F': F}

def buscar_recorridos(nodo, ruta_actual):
    ruta = ruta_actual + [nodo]
    
    # Nodos finales
    if nodo == 'D' or nodo == 'F':
        print("-".join(ruta).lower())
        return
        
    # Recorremos el conjunto correspondiente
    for destino in grafo[nodo]:
        if destino not in ruta:
            buscar_recorridos(destino, ruta)

print("Rutas posibles:")
buscar_recorridos('A', [])