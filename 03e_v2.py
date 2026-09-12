# ==========================================================
# SISTEMA DE AUTORIZACIÓN PARA EXAMEN
# Mostrar texto citado


print("=" * 55)
print("       SISTEMA DE AUTORIZACIÓN PARA EXAMEN")
print("=" * 55)

asistencia = float(input("Ingresa el porcentaje de asistencia: "))
promedio = float(input("Ingresa el promedio: "))

proyecto = input(
    "¿Entregó el proyecto? (si/no): "
).lower()

adeudos = input(
    "¿Tiene adeudos? (si/no): "
).lower()

autorizacion = input(
    "¿Tiene autorización especial? (si/no): "
).lower()

lista_oficial = input(
    "¿Aparece en la lista oficial? (si/no): "
).lower()


# 2. PROPOSICIONES
# ----------------------------------------------------------

# P = Tiene asistencia suficiente
P = asistencia >= 80

# Q = Tiene promedio aprobatorio
Q = promedio >= 7

# R = Entregó el proyecto
R = proyecto == "si"

# S = NO tiene adeudos
S = adeudos == "no"

# T = Tiene autorización especial
T = autorizacion == "si"

# U = Aparece en la lista oficial
U = lista_oficial == "si"


# ----------------------------------------------------------
# 3. MOSTRAR PROPOSICIONES
# ----------------------------------------------------------

print("\n" + "=" * 55)
print("           PROPOSICIONES")
print("=" * 55)

print("P - Asistencia suficiente :", P)
print("Q - Promedio aprobatorio :", Q)
print("R - Proyecto entregado   :", R)
print("S - Sin adeudos          :", S)
print("T - Autorización especial:", T)
print("U - Está en lista oficial:", U)


# ----------------------------------------------------------
# 4. NEGACIÓN
# ----------------------------------------------------------

no_U = not U

print("\nNEGACIÓN")
print("¬U - NO está en lista oficial:", no_U)


# ----------------------------------------------------------
# 5. CONJUNCIÓN
# ----------------------------------------------------------

conjuncion = P and Q

print("\nCONJUNCIÓN")
print("P ∧ Q =", conjuncion)


# ----------------------------------------------------------
# 6. DISYUNCIÓN
# ----------------------------------------------------------

disyuncion = Q or T

print("\nDISYUNCIÓN")
print("Q ∨ T =", disyuncion)


# ----------------------------------------------------------
# 7. CONDICIONAL
# ----------------------------------------------------------

# P → Q
#
# Se puede expresar como:
#
# (NOT P) OR Q

condicional = (not P) or Q

print("\nCONDICIONAL")
print("P → Q =", condicional)


# ----------------------------------------------------------
# 8. BICONDICIONAL
# ----------------------------------------------------------

# T ↔ U
#
# La autorización especial y la presencia
# en la lista deben coincidir.

bicondicional = T == U

print("\nBICONDICIONAL")
print("T ↔ U =", bicondicional)


# ----------------------------------------------------------
# 9. REGLA PRINCIPAL
# ----------------------------------------------------------

# IMPORTANTE:
#
# U DEBE SER VERDADERA.
#
# Es decir:
#
# El alumno DEBE estar en la lista oficial.
#
# Después debe cumplir:
#
# (P AND Q AND R AND S)
#
# O tener:
#
# T = autorización especial
#
# Expresión completa:
#
# U AND ((P AND Q AND R AND S) OR T)

resultado = U and ((P and Q and R and S) or T)


# ----------------------------------------------------------
# 10. DECISIÓN FINAL
# ----------------------------------------------------------

print("\n" + "=" * 55)
print("                RESULTADO")
print("=" * 55)

if not U:
    print("El alumno NO aparece en la lista oficial.")
    print("NO PUEDE PRESENTAR EL EXAMEN.")

elif resultado:
    print("El alumno cumple los requisitos.")
    print("PUEDE PRESENTAR EL EXAMEN.")

else:
    print("El alumno aparece en la lista oficial,")
    print("pero NO cumple los demás requisitos.")
    print("NO PUEDE PRESENTAR EL EXAMEN.")