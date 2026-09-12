# ==========================================================
# CASO DE ESTUDIO
# Sistema para revisar funcionalidad de laptop
# ==========================================================

print("=" * 55)
print("       SISTEMA para revisar laptop")
print("=" * 55)

# ----------------------------------------------------------
# 1. ENTRADA DE DATOS
# ----------------------------------------------------------


electricidad = input(
    "¿Tiene electricidad? (si/no): "
).lower()

enciende = input(
    "¿Se enciende? (si/no): "
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

# ----------------------------------------------------------
# 3. MOSTRAR LAS PROPOSICIONES
# ----------------------------------------------------------

print("\n" + "=" * 55)
print("Respuestas a las preguntas de diagnostico")
print("=" * 55)

print("e - Tiene electricidad   :", e)
print("n - Se enciende          :", n)
print("a - Da imagen            :", a)
print("z - No aparece azul      :", z)
print("p - No parpadea          :", p)
print("d - Drivers actualizados :", d)
print("fondo - Se ve el fondo de pantalla :", f)

if not e:
    print("\nLa laptop no tiene electricidad, revisar alimentacion.")
elif not n:
    print("\nLa laptop no se enciende, revisar fuente de poder.")
elif not a:
    print("\nLa laptop no da imagen, revisar pantalla o memoria.")
elif not z and not p:
    print("\nLa laptop aparece azul de error y parpadea la pantalla, revisar sistema operativo y pantalla.")
elif not z:
    print("\nLa laptop aparece azul de error, revisar sistema operativo.")
elif not d or not p:
    print("\nLa laptop tiene problemas de drivers y parpadeo, actualizar drivers y revisar pantalla.")
elif d and not p:
    print("\nLa laptop tiene drivers actualizados pero parpadea la pantalla, revisar pantalla.")
elif not fondo and not d:
    print("\nLa laptop no muestra el fondo de pantalla y los drivers no estan actualizados, revisar configuracion de pantalla y actualizar drivers.")
elif not fondo:
    print("\nLa laptop no muestra el fondo de pantalla, revisar configuracion de pantalla peo funciona correctamente.")
else:
    print("\nLa laptop funciona correctamente.")

