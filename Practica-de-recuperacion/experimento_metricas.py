import time
import matplotlib.pyplot as plt
from clasificador_ia import procesar_incidente, clasificador_estatico_respaldo

# ==========================================
# DATASET: 30 Correos de Prueba Etiquetados
# ==========================================
dataset = [
    # Fallas Mecánicas (10)
    {"texto": "El camión AAA-111 tiene el motor sobrecalentado y no enciende.", "label": "Falla Mecánica"},
    {"texto": "Se ponchó una llanta de la unidad BBB-222 en el andén norte.", "label": "Falla Mecánica"},
    {"texto": "Falla mecánica grave, la transmisión del trailer falló.", "label": "Falla Mecánica"},
    {"texto": "Problemas de motor con la unidad CCC-333, humo saliendo del cofre.", "label": "Falla Mecánica"},
    {"texto": "Batería muerta en el montacargas principal, ocupamos soporte.", "label": "Falla Mecánica"},
    {"texto": "El camión reporta pérdida de frenos en la rampa de acceso.", "label": "Falla Mecánica"},
    {"texto": "Fuga de aceite detectada debajo de la unidad DDD-444.", "label": "Falla Mecánica"},
    {"texto": "El sistema hidráulico de la caja no responde.", "label": "Falla Mecánica"},
    {"texto": "Se rompió la banda del motor del camión EEE-555.", "label": "Falla Mecánica"},
    {"texto": "Check engine encendido, pérdida de potencia en andén 2.", "label": "Falla Mecánica"},
    
    # Accidentes Graves (10)
    {"texto": "Choque aparatoso en la entrada principal, hay lesiones.", "label": "Accidente Grave"},
    {"texto": "Urgente: Accidente, un montacargas volcó y el operador está herido.", "label": "Accidente Grave"},
    {"texto": "El trailer FFF-666 colisionó contra la pluma de seguridad.", "label": "Accidente Grave"},
    {"texto": "Ambulancia requerida, lesión grave por aplastamiento en bodega.", "label": "Accidente Grave"},
    {"texto": "Accidente múltiple: dos camiones chocaron por alcance.", "label": "Accidente Grave"},
    {"texto": "Atropellamiento leve en zona de carga, operador con lesión.", "label": "Accidente Grave"},
    {"texto": "Choque contra el muro de contención, posible fuga de combustible.", "label": "Accidente Grave"},
    {"texto": "Derrumbe de rack sobre un montacargas, accidente crítico.", "label": "Accidente Grave"},
    {"texto": "El camión GGG-777 se estrelló maniobrando en reversa.", "label": "Accidente Grave"},
    {"texto": "Impacto fuerte, el conductor tiene una lesión en la cabeza.", "label": "Accidente Grave"},
    
    # Retrasos / Reportes Generales (10)
    {"texto": "Retraso operativo, hay mucha fila en la caseta 3.", "label": "Retraso Operativo"},
    {"texto": "El proveedor va a llegar tarde, pidió una espera de 2 horas.", "label": "Retraso Operativo"},
    {"texto": "Largo tiempo de espera por falta de personal en aduana.", "label": "Retraso Operativo"},
    {"texto": "Se reporta retraso por lluvia fuerte en la ruta.", "label": "Retraso Operativo"},
    {"texto": "El operador HHH-888 llegará tarde por tráfico denso.", "label": "Retraso Operativo"},
    {"texto": "Esperando autorización de acceso desde hace media hora.", "label": "Retraso Operativo"},
    {"texto": "Retraso en la descarga, no hay andenes disponibles.", "label": "Retraso Operativo"},
    {"texto": "El camión no trae los papeles completos, en espera.", "label": "Retraso Operativo"},
    {"texto": "Llegada tarde confirmada por el supervisor de turno.", "label": "Retraso Operativo"},
    {"texto": "Todo en orden, solo un ligero retraso en el papeleo.", "label": "Retraso Operativo"}
]

# ==========================================
# EJECUCIÓN Y MEDICIÓN
# ==========================================
aciertos_hibrido = 0
aciertos_estatico = 0
latencias = []
y_true = []
y_pred = []

print("Iniciando experimento con 30 correos... (Esto tomará un par de minutos)")

for i, data in enumerate(dataset):
    print(f"Procesando correo {i+1}/30...")
    texto = data["texto"]
    label_real = data["label"]
    y_true.append(label_real)
    
    # Evaluar Modelo Estático Tradicional
    res_estatico = clasificador_estatico_respaldo(texto)
    if res_estatico["clasificacion"] == label_real:
        aciertos_estatico += 1
        
    # Evaluar Modelo Híbrido (LLM) y medir Latencia
    inicio = time.time()
    res_hibrido = procesar_incidente(texto) # LLM con respaldo
    fin = time.time()
    
    latencias.append(fin - inicio)
    clasificacion_ia = res_hibrido.get("clasificacion", "Desconocida")
    y_pred.append(clasificacion_ia)
    
    # Consideramos acierto si el modelo logró captar la categoría general
    if label_real.lower() in clasificacion_ia.lower() or clasificacion_ia.lower() in label_real.lower():
        aciertos_hibrido += 1

# ==========================================
# RESULTADOS Y GRÁFICAS
# ==========================================
exactitud_estatico = (aciertos_estatico / 30) * 100
exactitud_hibrido = (aciertos_hibrido / 30) * 100
latencia_promedio = sum(latencias) / len(latencias)

print("\n--- RESULTADOS DEL EXPERIMENTO ---")
print(f"Exactitud Estática (Reglas): {exactitud_estatico}%")
print(f"Exactitud Híbrida (LLM + Reglas): {exactitud_hibrido}%")
print(f"Latencia promedio por correo: {latencia_promedio:.2f} segundos")

# Crear Gráfica Comparativa y de Latencias
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Gráfico 1: Exactitud
barras = ax1.bar(['Reglas Estáticas', 'Híbrido (Llama 3.2)'], [exactitud_estatico, exactitud_hibrido], color=['#EF4444', '#10B981'])
ax1.set_title('Comparativa de Exactitud (30 Correos)', fontweight="bold")
ax1.set_ylabel('Porcentaje de Aciertos (%)')
ax1.set_ylim(0, 110)
for barra in barras:
    yval = barra.get_height()
    ax1.text(barra.get_x() + barra.get_width()/2, yval + 2, f"{yval:.1f}%", ha='center', va='bottom', fontweight="bold")

# Gráfico 2: Latencia
ax2.plot(range(1, 31), latencias, marker='o', color='#3B82F6', linewidth=2)
ax2.set_title(f'Latencia del LLM local (Promedio: {latencia_promedio:.2f}s)', fontweight="bold")
ax2.set_xlabel('Número de Correo Procesado')
ax2.set_ylabel('Tiempo de respuesta (Segundos)')
ax2.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.show()