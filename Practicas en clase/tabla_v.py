def a_letra(valor):
    return "V" if valor else "F"

# Encabezado
print(f"{'P':^5} | {'Q':^5} | {'¬P':^5} | {'P∧Q':^5} | {'P∨Q':^5} | {'P→Q':^5} | {'P↔Q':^5}")
print("-" * 53)

# combinaciones de P y Q
combinaciones = [
    (True, True),
    (True, False),
    (False, True),
    (False, False)
]

for p, q in combinaciones:
    neg_p = not p
    conjuncion = p and q
    disyuncion = p or q
    condicional = (not p) or q
    bicondicional = (p == q)

    print(f"{a_letra(p):^5} | {a_letra(q):^5} | {a_letra(neg_p):^5} | {a_letra(conjuncion):^5} | {a_letra(disyuncion):^5} | {a_letra(condicional):^5} | {a_letra(bicondicional):^5}")