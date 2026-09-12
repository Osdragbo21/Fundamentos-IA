import random
# ==========================================================
# CASO DE ESTUDIO
# Sistema para revisar funcionalidad de dispositivos (PC, Laptop, Servidor, tablet)
# ==========================================================

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

dispositivo = input("Ingrese el tipo de dispositivo: ")

# ----------------------------------------------------------
# 1. ENTRADA DE DATOS
# ----------------------------------------------------------


electricidad = input(
    "¿Tiene electricidad? (si/no): "
).lower()

enciende = input(
    "¿Se puede encender? (si/no): "
).lower()

imagen = input(
    "¿Da imagen? (si/no): "
).lower()

azul = input(
    "¿Aparece una pantalla azul de error? (si/no): "
).lower()

parpadeo = input(
    "¿Parpadea la pantalla? (si/no): "
).lower()

drivers = input(
    "¿Se han actualizado los drivers? (si/no): "
).lower()

fondo = input(
    "¿Se ve el fondo de pantalla? (si/no): "
).lower()

# ----------------------------------------------------------
# 2. CREACIÓN DE LAS PROPOSICIONES
# ----------------------------------------------------------

e = electricidad == "si"

n = enciende == "si"

a = imagen == "si"

z = azul == "no"

p = parpadeo == "no"

d = drivers == "si"

f = fondo == "si"

# Tiket random para pruebas

t = random.randint(1, 100)

# ----------------------------------------------------------
# 3. Impresion y no de reporte
# ----------------------------------------------------------

print("\n" + "=" * 55)
print("Tiket de diagnostico de dispositivo")
print("Su numero de tiket es:", t)
print("=" * 55)

print("Usuario:", usuario)
print("Nombre:", nombre)
print("Direccion:", direccion)
print("Dispositivo:", dispositivo)

print("\n" + "=" * 55)
print("Las respuestas a las preguntas de diagnostico")
print("=" * 55)

print("e - Tiene electricidad   :", e)
print("n - Se puede encender    :", n)
print("a - Da imagen            :", a)
print("z - No aparece azul      :", z)
print("p - No parpadea          :", p)
print("d - Drivers actualizados :", d)
print("f - Se ve el fondo de pantalla :", f)

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
elif not fondo and not d:
    print("\nLa laptop no muestra el fondo de pantalla y los drivers no estan actualizados, revisar configuracion de pantalla y actualizar drivers.")
elif not fondo:
    print("\nLa laptop no muestra el fondo de pantalla, revisar configuracion de pantalla peo funciona correctamente.")
else:
    print("\nLa laptop funciona correctamente.")