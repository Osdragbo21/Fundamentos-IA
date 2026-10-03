import random
from datetime import datetime

t = random.randint(1, 100)
k = "C" + str(t)
fecha = datetime.now().strftime("%Y-%m-%d")
hora = datetime.now().strftime("%H:%M:%S")

# ============================================
# SISTEMA EXPERTO DE DIAGNÓSTICO
# ============================================
#Agregar más preguntas para el diagnóstico de pasientes
#Variables de edad, genero, adicciones, habitos de sueño, historial médico, síntomas específicos, etc.

print("SISTEMA DE DIAGNÓSTICO")

nombre = input("Ingrese el nombre del pasiente: ")
direccion = input("Ingrese direccion del pasiente: ")

fiebre = input("¿Tiene fiebre? (s/n): ")
tos = input("¿Tiene tos? (s/n): ")
dolor = input("¿Tiene dolor de garganta? (s/n): ")

if fiebre == "s" and tos == "s":
    diagnostico = "Posible infección respiratoria"

elif tos == "s" and dolor == "s":
    diagnostico = "Posible irritación respiratoria"

elif fiebre == "s":
    diagnostico = "Se recomienda valoración profesional"

else:
    print("No se identifico un patrón")
    continuar = input("Continuar con el diagnóstico de otras condiciones (s/n): ")
    if continuar == "s":
        dolor_cabeza = input("¿Tiene dolor de cabeza? (s/n): ")
        cansancio = input("¿Se siente cansado? (s/n): ")
        if dolor_cabeza == "s" and cansancio == "s":
            diagnostico = "Posible migraña o fatiga"
        elif dolor_cabeza == "s":
            diagnostico = "Posible cefalea"
        elif cansancio == "s":
            diagnostico = "Posible fatiga"
        else:
            diagnostico = "No se identificó un patrón"
    else:
        diagnostico = "No se identificó un patrón"


#Ficha de diagnostico

print("\n" + "=" * 55)
print("Ficha de diagnostico")
print("Fecha:", fecha)
print("Hora:", hora)
print("Su numero de consulta es:", k)
print("=" * 55)

print("Nombre:", nombre)
print("Direccion:", direccion)
print("=" * 55)

print("Resultado:")
print(diagnostico)
print("=" * 55)

