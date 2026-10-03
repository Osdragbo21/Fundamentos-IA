from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class Camion(BaseModel):
    placa: str
    camion_id: str
    empresa: str
    autorizacion: bool
    certificacion_conductor: bool

class Acceso(BaseModel):
    placa: str
    P: bool
    Q: bool
    R: bool
    S: bool
    # Nuevas variables que agregaremos en la Fase 2:
    # T: bool (Horario permitido)
    # U: bool (Seguro vigente)
    resultado_A: bool
    resultado_E: bool
    operador: str
    marca_tiempo: datetime = Field(default_factory=datetime.now)
    explicacion_paso_a_paso: List[str]

class Incidente(BaseModel):
    correo_original: str
    clasificacion: str
    prioridad: str
    datos_extraidos: Dict[str, Any]
    estado: str = Field(default="nuevo") # nuevo, en_atencion, cerrado
    fecha_reporte: datetime = Field(default_factory=datetime.now)

class RiesgoEticoModel(BaseModel):
    modulo: str
    descripcion: str
    categoria: str
    probabilidad: int
    impacto: int
    mitigacion: str
    historico_cambios: List[str] = Field(default_factory=list)

class EvaluacionLLM(BaseModel):
    prompt: str
    respuesta: str
    modelo: str
    latencia_ms: float
    coincidio_con_reglas: bool
    fecha_evaluacion: datetime = Field(default_factory=datetime.now)