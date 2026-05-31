from collections import OrderedDict
from typing import Optional
from pydantic import BaseModel


class PersonaRespuesta(BaseModel):
    mot_visita: str = ""
    mot_visita2: str = ""
    tipo_visita: Optional[str] = None
    parentesco: str = ""
    respuestas: list[list[str]] = []


class VisitaItem(BaseModel):
    cod_pregunta: int = 0
    id_modulo: int = 0
    valor: str = ""


class DetalleProgramacion(BaseModel):
    id_persona: str
    mot_visita: str = ""
    mot_visita2: str = ""


class ProgramacionData(BaseModel):
    id_programacion: int
    estado: str = "A"
    direccion: str = ""
    otradir: str = ""
    barrio: str = ""
    id_barrio: Optional[int] = None
    telefono1: str = ""
    telefono2: str = ""
    latitud: str = ""
    longitud: str = ""
    dpto: str = ""
    municipio: str = ""
    id_desplazamiento: str = ""
    orden: Optional[int] = None
    personas: dict[str, PersonaRespuesta] = {}
    visita: list[list] = []


def build_programacion_dict(prog: ProgramacionData) -> OrderedDict:
    d = OrderedDict()
    d["ID_PROGRAMACION"] = prog.id_programacion
    d["ESTADO"] = prog.estado if prog.estado else "A"
    d["DIRECCION"] = prog.direccion if prog.direccion else ""
    d["OTRADIR"] = prog.otradir if prog.otradir else ""
    d["BARRIO"] = prog.barrio if prog.barrio else ""
    d["ID_BARRIO"] = prog.id_barrio
    d["TELEFONO1"] = prog.telefono1 if prog.telefono1 else ""
    d["TELEFONO2"] = prog.telefono2 if prog.telefono2 else ""
    d["LATITUD"] = prog.latitud if prog.latitud else ""
    d["LONGITUD"] = prog.longitud if prog.longitud else ""
    d["DPTO"] = prog.dpto if prog.dpto else ""
    d["MUNICIPIO"] = prog.municipio if prog.municipio else ""
    d["ID_DESPLAZAMIENTO"] = prog.id_desplazamiento if prog.id_desplazamiento else ""
    d["ORDEN"] = prog.orden

    personas_dict = OrderedDict()
    for pid, p in (prog.personas or {}).items():
        pd = OrderedDict()
        pd["MOTVISITA"] = p.mot_visita if p.mot_visita else ""
        pd["MOTVISITA2"] = p.mot_visita2 if p.mot_visita2 else ""
        pd["TIPOVISITA"] = p.tipo_visita
        pd["PARENTESCO"] = p.parentesco if p.parentesco else ""
        if p.respuestas:
            pd["RESPUESTAS"] = p.respuestas
        personas_dict[pid] = pd
    d["PERSONAS"] = personas_dict if personas_dict else {}
    d["VISITA"] = prog.visita if prog.visita else []

    return d


def build_programacion_response(
    programaciones: list[ProgramacionData],
) -> OrderedDict:
    body = OrderedDict()
    body["PROGRAMACION"] = [
        build_programacion_dict(p) for p in programaciones
    ]
    return body


def build_error_response(error_msg: str) -> OrderedDict:
    body = OrderedDict()
    body["ERROR"] = error_msg
    return body


def build_legacy_headers(
    fecha_sync: str,
    cantidad_registros: Optional[int] = None,
) -> dict[str, str]:
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Expires": "0",
        "Cache-Control": "must-revalidate, post-check=0, pre-check=0",
        "Content-Disposition": "inline; filename=Programacion.json; name=Programacion.json",
    }
    headers["X-Cache-Control-Private"] = "private"
    if fecha_sync:
        headers["FECHA_SYNC"] = fecha_sync
    if cantidad_registros is not None:
        headers["CANTIDAD_REGISTROS"] = str(cantidad_registros)
    return headers
