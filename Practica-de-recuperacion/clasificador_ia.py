import json
import logging
import ollama
from models import Incidente
from database import incidentes_col

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("logismart_ia")

MODELO = "llama3.2:1b"

def clasificador_estatico_respaldo(correo: str) -> dict:
    """Clasificador tradicional basado en reglas. Se activa si el LLM falla."""
    correo_min = correo.lower()
    if "choque" in correo_min or "accidente" in correo_min or "lesión" in correo_min:
        return {"clasificacion": "Accidente Grave", "prioridad": "Alta", "datos_extraidos": {"metodo": "estatico"}}
    elif "retraso" in correo_min or "tarde" in correo_min or "espera" in correo_min:
        return {"clasificacion": "Retraso Operativo", "prioridad": "Baja", "datos_extraidos": {"metodo": "estatico"}}
    elif "falla" in correo_min or "ponchada" in correo_min or "motor" in correo_min:
        return {"clasificacion": "Falla Mecánica", "prioridad": "Media", "datos_extraidos": {"metodo": "estatico"}}
    else:
        return {"clasificacion": "Reporte General", "prioridad": "Media", "datos_extraidos": {"metodo": "estatico"}}

def procesar_incidente(correo_texto: str) -> dict:
    """Extrae información del correo usando IA generativa y la guarda en MongoDB."""
    prompt = f"""
    Extrae la información del correo y responde ÚNICAMENTE con un JSON estricto.
    - clasificacion: tipo de problema (ej. Falla Mecánica, Accidente, Retraso).
    - prioridad: Alta, Media o Baja.
    - placa: extrae la placa del vehículo (o null si no hay).
    - ubicacion: extrae el lugar del incidente (o null si no hay).

    Formato exacto esperado:
    {{
        "clasificacion": "valor",
        "prioridad": "valor",
        "datos_extraidos": {{"placa": "valor", "ubicacion": "valor"}}
    }}

    Correo: "{correo_texto}"
    """
    
    incidente_validado = None
    
    try:
        # Llamada a la IA forzando formato JSON
        respuesta = ollama.chat(model=MODELO, messages=[{"role": "user", "content": prompt}], format="json")
        contenido_llm = respuesta["message"]["content"]
        
        datos_extraidos_llm = json.loads(contenido_llm)
        
        # Validación estricta con Pydantic
        incidente_validado = Incidente(
            correo_original=correo_texto,
            clasificacion=datos_extraidos_llm.get("clasificacion", "Desconocida"),
            prioridad=datos_extraidos_llm.get("prioridad", "Media"),
            datos_extraidos=datos_extraidos_llm.get("datos_extraidos", {})
        )
        log.info("Clasificación por LLM exitosa.")
        
    except Exception as e:
        log.warning(f"El LLM falló. Activando respaldo estático. Error: {e}")
        datos_respaldo = clasificador_estatico_respaldo(correo_texto)
        incidente_validado = Incidente(
            correo_original=correo_texto,
            clasificacion=datos_respaldo["clasificacion"],
            prioridad=datos_respaldo["prioridad"],
            datos_extraidos=datos_respaldo["datos_extraidos"]
        )
        
    # Persistencia en la base de datos
    datos_dict = incidente_validado.model_dump()
    try:
        if incidentes_col is not None:
            incidentes_col.insert_one(datos_dict)
            log.info("Incidente guardado en MongoDB.")
    except Exception as e_bd:
        log.error(f"Error crítico al guardar en MongoDB: {e_bd}")
        
    return datos_dict