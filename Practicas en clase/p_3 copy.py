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

# Nuevas variables para ampliar el diagnóstico
edad = int(input("Ingrese la edad del paciente: "))
genero = input("Ingrese el género del paciente (M/F/O): ").strip().lower()
adiccion = input("¿Tiene alguna adicción? (s/n): ").strip().lower()
sueno = input("¿Tiene hábitos de sueño regulares? (s/n): ").strip().lower()
historial = input("¿Tiene historial médico previo? (s/n): ").strip().lower()

fiebre = input("¿Tiene fiebre? (s/n): ").strip().lower()
tos = input("¿Tiene tos? (s/n): ").strip().lower()
dolor = input("¿Tiene dolor de garganta? (s/n): ").strip().lower()

# Respuestas posibles para cada variable
respuesta_edad = ""
if edad >= 65:
    respuesta_edad = "Paciente adulto mayor"
elif edad >= 18:
    respuesta_edad = "Paciente adulto"
else:
    respuesta_edad = "Paciente joven"

respuesta_genero = ""
if genero == "m":
    respuesta_genero = "Género masculino"
elif genero == "f":
    respuesta_genero = "Género femenino"
else:
    respuesta_genero = "Género no especificado"

respuesta_adiccion = ""
if adiccion == "s":
    respuesta_adiccion = "Tiene adicción"
else:
    respuesta_adiccion = "No reporta adicción"

respuesta_sueno = ""
if sueno == "s":
    respuesta_sueno = "Tiene sueño regular"
else:
    respuesta_sueno = "No tiene sueño regular"

respuesta_historial = ""
if historial == "s":
    respuesta_historial = "Tiene historial médico"
else:
    respuesta_historial = "No tiene historial médico"

# Lógica del diagnóstico usando and, or y not
if (fiebre == "s" and tos == "s") or (tos == "s" and dolor == "s"):
    diagnostico = "Posible infección respiratoria o irritación respiratoria"

elif fiebre == "s" and not (tos == "s" or dolor == "s"):
    diagnostico = "Se recomienda valoración profesional"

elif tos == "s" and not fiebre == "s":
    diagnostico = "Posible irritación respiratoria"

else:
    print("No se identifico un patrón")
    continuar = input("Continuar con el diagnóstico de otras condiciones (s/n): ")
    if continuar == "s":
        dolor_cabeza = input("¿Tiene dolor de cabeza? (s/n): ").strip().lower()
        cansancio = input("¿Se siente cansado? (s/n): ").strip().lower()
        if dolor_cabeza == "s" and cansancio == "s":
            diagnostico = "Posible migraña o fatiga"
        elif dolor_cabeza == "s" or cansancio == "s":
            diagnostico = "Posible cefalea o fatiga"
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
print("Edad:", respuesta_edad)
print("Género:", respuesta_genero)
print("Adicción:", respuesta_adiccion)
print("Sueño:", respuesta_sueno)
print("Historial:", respuesta_historial)
print("=" * 55)

print("Resultado:")
print(diagnostico)
print("=" * 55)

