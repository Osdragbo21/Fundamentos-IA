from typing import Dict, Any
from models import Acceso
from database import accesos_col
import logging

# Configuración del log
log = logging.getLogger("logismart_reglas")

def evaluar_camion_extendido(placa: str, operador: str, P: bool, Q: bool, R: bool, S: bool, T: bool, U: bool) -> Dict[str, Any]:
    explicacion = []

    # 1. Reglas lógicas extendidas
    A = P and S and (not Q) and T and U
    E = P and (R or Q)

    # 2. Generación de trazabilidad explicativa (Paso a paso)
    if R and not U:
        explicacion.append("[CRÍTICO] Contradicción/Riesgo: Se reporta carga peligrosa (R) sin seguro vigente (U).")
    
    if not P:
        explicacion.append("[X] Acceso denegado de inmediato: El vehículo NO cuenta con autorización previa (P).")
        A, E = False, False
    else:
        explicacion.append("[OK] El vehículo cuenta con autorización previa (P).")
        
        # Evaluación del Acceso Estándar (A)
        if A:
            explicacion.append("[OK] Se autoriza ACCESO ESTÁNDAR: Cumple certificación, peso correcto, horario y seguro.")
        else:
            if not S: explicacion.append("[X] Fallo Acceso: La certificación del conductor no está vigente (S).")
            if Q: explicacion.append("[X] Fallo Acceso: El vehículo presenta exceso de peso (Q).")
            if not T: explicacion.append("[X] Fallo Acceso: El vehículo está fuera del horario permitido (T).")
            if not U: explicacion.append("[X] Fallo Acceso: El seguro de la unidad no está vigente (U).")

        # Evaluación de Inspección Especial (E)
        if E:
            if R: explicacion.append("[!] Se requiere INSPECCIÓN ESPECIAL por presencia de materiales peligrosos (R).")
            elif Q: explicacion.append("[!] Se requiere INSPECCIÓN ESPECIAL por exceso de peso (Q).")

    # 3. Modelado de datos con Pydantic
    registro = Acceso(
        placa=placa, 
        P=P, Q=Q, R=R, S=S, T=T, U=U,
        resultado_A=A, 
        resultado_E=E, 
        operador=operador,
        explicacion_paso_a_paso=explicacion
    )
    
    datos_dict = registro.model_dump()
    
    # 4. Persistencia en MongoDB
    try:
        if accesos_col is not None:
            accesos_col.insert_one(datos_dict)
            log.info(f"Registro de acceso guardado en BD para placa {placa}")
    except Exception as err:
        log.error(f"Error al guardar en MongoDB: {err}")

    return datos_dict

if __name__ == "__main__":
    print("Probando motor de reglas y guardado en MongoDB...")
    resultado = evaluar_camion_extendido(
        placa="DEF-456", operador="Osvaldo Salinas", 
        P=True, Q=False, R=True, S=True, T=True, U=False
    )
    
    print("\nResultados:")
    print(f"Acceso Estándar (A): {resultado['resultado_A']}")
    print(f"Inspección Especial (E): {resultado['resultado_E']}")
    print("\nExplicación generada:")
    for paso in resultado["explicacion_paso_a_paso"]:
        print(f" - {paso}")