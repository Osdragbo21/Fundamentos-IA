import random
from datetime import datetime

t = random.randint(1, 100)
k = "t" + str(t)
fecha = datetime.now().strftime("%Y-%m-%d")
hora = datetime.now().strftime("%H:%M:%S")

# ==========================================================
# CASO DE ESTUDIO
# Sistema para revisar funcionalidad de dispositivos (PC, Laptop, Servidor, tablet)
# ==========================================================
# Bienvenida
# ==========================================================
print("=" * 55)
print("Bienvenido al sistema de diagnostico de dispositivos")
print("=" * 55)
print("Para continuar se realizaran unas preguntas de formalidad")
print("=" * 55)
# ----------------------------------------------------------
# ENTRADA DE DATOS de usuario
# ----------------------------------------------------------
usuario = input("Ingrese su nombre de usuario: ")
nombre = input("Ingrese su nombre: ")
direccion = input("Ingrese su direccion: ")
print("Dispositivos disponibles:")
print("1. PC")
print("2. Laptop") 
print("3. Servidor")
print("4. Tablet")
opcion = input("Seleccione el tipo de dispositivo (1-4): ")
if opcion == "1":
    dispositivo = "PC"
elif opcion == "2":
    dispositivo = "Laptop"
elif opcion == "3":
    dispositivo = "Servidor"
elif opcion == "4":
    dispositivo = "Tablet"
else:
    print("Opción inválida. Se asignará 'Desconocido' como tipo de dispositivo.")
    dispositivo = "Desconocido"

# ----------------------------------------------------------
# 1. ENTRADA DE DATOS
# ----------------------------------------------------------
print("\n" + "=" * 55)
print("           PROCESO DE DIAGNOSTICO")
print("=" * 55)

electricidad = input(
    "¿Tiene electricidad? (si/no): "
).lower()
e = electricidad == "si"
if e:
    enciende = input(
        "¿Se puede encender? (si/no): "
    ).lower()
    n = enciende == "si"

    if n:
        imagen = input(
            "¿Da imagen? (si/no): "
        ).lower()
        a = imagen == "si"

        if a:
            azul = input(
                "¿Aparece una pantalla azul de error? (si/no): "
            ).lower()
            z = azul == "no"

            if z:
                parpadeo = input(
                    "¿Parpadea la pantalla? (si/no): "
                ).lower()
                p = parpadeo == "no"

                drivers = input(
                    "¿Se han actualizado los drivers? (si/no): "
                ).lower()
                d = drivers == "si"



# ----------------------------------------------------------
# 3. Impresion y no de reporte
# ----------------------------------------------------------

print("\n" + "=" * 55)
print("Tiket de diagnostico de dispositivo")
print("Fecha:", fecha)
print("Hora:", hora)
print("Su numero de tiket es:", k)
print("=" * 55)

print("Usuario:", usuario)
print("Nombre:", nombre)
print("Direccion:", direccion)
print("Dispositivo:", dispositivo)

print("\n" + "=" * 55)
print("Las respuestas a las preguntas de diagnostico")
print("=" * 55)

print("e - Tiene electricidad   :", e)
if e:
    print("n - Se puede encender    :", n)
    if n:
        print("a - Da imagen            :", a)
        if a:
            print("z - No aparece azul      :", z)
            if z:
                print("p - No parpadea          :", p)
                print("d - Drivers actualizados :", d)

print("\n" + "=" * 55)
print("La solucion al diagnostico de su dispositivo es la siguiente:")
print("=" * 55)

if not e:
    print("\nEl dispositivo no tiene electricidad, revisar alimentacion.")
elif not n:
    print("\nEl dispositivo no se enciende, revisar fuente de poder.")
elif not a:
    print("\nEl dispositivo no da imagen, revisar pantalla o memoria.")
elif not z and not p:
    print("\nEl dispositivo aparece azul de error y parpadea la pantalla, revisar sistema operativo y pantalla.")
elif not z:
    print("\nEl dispositivo aparece azul de error, revisar sistema operativo.")
elif not d or not p:
    print("\nEl dispositivo tiene problemas de drivers y parpadeo, actualizar drivers y revisar pantalla.")
elif d and not p:
    print("\nLa laptop tiene drivers actualizados pero parpadea la pantalla, revisar pantalla.")
else:
    print("\nLa laptop funciona correctamente.")