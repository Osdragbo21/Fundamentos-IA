from typing import Dict, Any
from models import Acceso
from database import accesos_col
import logging

log = logging.getLogger("logismart_reglas")

def evaluar_camion_extendido(placa: str, operador: str, P: bool, Q: bool, R: bool, S: bool, T: bool, U: bool) -> Dict[str, Any]:
    """
    Evalúa el acceso con 6 variables, genera explicación y guarda en MongoDB.
    """
    explicacion = []

    # RETO OPCIONAL: Detección de contradicciones
    # Si un operador marca que tiene materiales peligrosos (R) pero NO tiene seguro (U), es un riesgo crítico.
    if R and not U:
        explicacion.append("[ALERTA] Contradicción/Riesgo: Se reporta carga peligrosa sin seguro vigente.")
    
    # Ecuaciones lógicas
    # A = P ∧ S ∧ ¬Q ∧ T ∧ U
    A = P and S and (not Q) and T and U
    
    # E = P ∧ (R ∨ Q)
    # Nota: Si el camión excede el peso o tiene material peligroso, va a inspección.
    E = P and (R or Q)

    # Construcción de la explicación paso a paso
    if not P:
        explicacion.append("❌ Acceso denegado de inmediato: El vehículo NO cuenta con autorización previa (P).")
        A, E = False, False
    else:
        explicacion.append("✅ El vehículo cuenta con autorización previa (P).")
        
        if A:
            explicacion.append("✅ Se autoriza ACCESO ESTÁNDAR: Cumple certificación, peso correcto, horario y seguro.")
        else:
            if not S: explicacion.append("❌ Fallo Acceso: La certificación del conductor no está vigente (S).")
            if Q: explicacion.append("❌ Fallo Acceso: El vehículo presenta exceso de peso (Q).")
            if not T: explicacion.append("❌ Fallo Acceso: El vehículo está fuera del horario permitido (T).")
            if not U: explicacion.append("❌ Fallo Acceso: El seguro de la unidad no está vigente (U).")

        if E:
            if R: explicacion.append("⚠️ Se requiere INSPECCIÓN ESPECIAL por presencia de materiales peligrosos (R).")
            elif Q: explicacion.append("⚠️ Se requiere INSPECCIÓN ESPECIAL por exceso de peso (Q).")

    # Crear el objeto con Pydantic para validar los datos
    registro = Acceso(
        placa=placa,
        P=P, Q=Q, R=R, S=S, T=T, U=U,
        resultado_A=A,
        resultado_E=E,
        operador=operador,
        explicacion_paso_a_paso=explicacion
    )
    
    # Convertir a diccionario y guardar en MongoDB
    datos_dict = registro.model_dump()
    
    try:
        if accesos_col is not None:
            accesos_col.insert_one(datos_dict)
            log.info(f"Registro de acceso guardado en BD para placa {placa}")
    except Exception as err:
        log.error(f"Error al guardar en MongoDB: {err}")

    return datos_dict

# Bloque de prueba (Solo se ejecuta si corres este archivo directamente)
if __name__ == "__main__":
    print("Probando motor de reglas y guardado en MongoDB...")
    # Caso de prueba: Camión sin seguro y con carga peligrosa
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