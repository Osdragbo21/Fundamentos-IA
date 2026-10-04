import json
import logging
import ollama
from models import Incidente
from database import incidentes_col
from datetime import datetime

# Configuración de logs
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("logismart_ia")

MODELO = "llama3.2:1b"

def clasificador_estatico_respaldo(correo: str) -> dict:
    """
    Clasificador tradicional basado en reglas.
    Se activa ÚNICAMENTE si el LLM falla, garantizando que el sistema nunca colapse.
    """
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
    """
    Toma un correo, lo envía al LLM para extraer información en JSON y lo guarda en MongoDB.
    Si el LLM falla, usa el respaldo estático.
    """
    prompt = f"""
    Extrae la información del correo y responde ÚNICAMENTE con un JSON estricto.
    - clasificacion: tipo de problema (ej. Falla Mecánica, Accidente).
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
        # 1. Llamada a la IA (Fase generativa)
        # Forzamos el formato JSON para evitar que el modelo responda con texto normal
        respuesta = ollama.chat(model=MODELO, messages=[{"role": "user", "content": prompt}], format="json")
        contenido_llm = respuesta["message"]["content"]
        
        # 2. Convertir string a diccionario de Python
        datos_extraidos_llm = json.loads(contenido_llm)
        
        # 3. Validación estricta con Pydantic
        incidente_validado = Incidente(
            correo_original=correo_texto,
            clasificacion=datos_extraidos_llm.get("clasificacion", "Desconocida"),
            prioridad=datos_extraidos_llm.get("prioridad", "Media"),
            datos_extraidos=datos_extraidos_llm.get("datos_extraidos", {})
        )
        log.info("Clasificación por LLM exitosa.")
        
    except Exception as e:
        # 4. Plan de contingencia (Enfoque híbrido)
        log.warning(f"El LLM falló o devolvió un JSON inválido. Activando respaldo estático. Error: {e}")
        datos_respaldo = clasificador_estatico_respaldo(correo_texto)
        
        incidente_validado = Incidente(
            correo_original=correo_texto,
            clasificacion=datos_respaldo["clasificacion"],
            prioridad=datos_respaldo["prioridad"],
            datos_extraidos=datos_respaldo["datos_extraidos"]
        )
        
    # 5. Persistencia en la nube
    try:
        datos_dict = incidente_validado.model_dump()
        if incidentes_col is not None:
            incidentes_col.insert_one(datos_dict)
            log.info("Incidente guardado en MongoDB (Colección: incidentes).")
        return datos_dict
    except Exception as e_bd:
        log.error(f"Error crítico al guardar en MongoDB: {e_bd}")
        return {}

# Bloque de prueba
if __name__ == "__main__":
    correo_prueba = "URGENTE: El camión con placas AAA-999 tuvo una falla en el motor justo en la pluma de acceso norte y está bloqueando a los demás."
    
    print("Enviando correo al LLM para su análisis...")
    resultado = procesar_incidente(correo_prueba)
    
    print("\n--- RESULTADO ESTRUCTURADO Y GUARDADO ---")
    print(json.dumps(resultado, indent=2, default=str))