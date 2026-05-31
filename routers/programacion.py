import json
import time
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from models.programacion import (
    ProgramacionData,
    PersonaRespuesta,
    build_programacion_response,
    build_error_response,
    build_legacy_headers,
)

router = APIRouter()

FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"

SUCCESS_DEFAULT = {
    "PROGRAMACION": [
        {
            "ID_PROGRAMACION": 12345,
            "ESTADO": "A",
            "DIRECCION": "Calle 123 #45-67",
            "OTRADIR": "",
            "BARRIO": "BARRIO EJEMPLO",
            "ID_BARRIO": 456,
            "TELEFONO1": "3001234567",
            "TELEFONO2": "",
            "LATITUD": "4.123456",
            "LONGITUD": "-74.123456",
            "DPTO": "11",
            "MUNICIPIO": "001",
            "ID_DESPLAZAMIENTO": "1",
            "ORDEN": 1,
            "PERSONAS": {
                "1001": {
                    "MOTVISITA": "12",
                    "MOTVISITA2": "12",
                    "TIPOVISITA": "AU",
                    "PARENTESCO": ""
                },
                "1002": {
                    "MOTVISITA": "5",
                    "MOTVISITA2": "12",
                    "TIPOVISITA": "AU",
                    "PARENTESCO": ""
                }
            },
            "VISITA": [
                ["1", "1", "2024-05-06"],
                ["2", "1", "Calle 123"],
                ["3", "1", "3001234567"],
                ["4", "1", "25"],
                ["5", "1", "001"]
            ]
        },
        {
            "ID_PROGRAMACION": 12346,
            "ESTADO": "A",
            "DIRECCION": "Carrera 8 #15-90",
            "OTRADIR": "Apto 301",
            "BARRIO": "EL PORVENIR",
            "ID_BARRIO": 789,
            "TELEFONO1": "3109876543",
            "TELEFONO2": "6012345678",
            "LATITUD": "4.654321",
            "LONGITUD": "-74.654321",
            "DPTO": "25",
            "MUNICIPIO": "001",
            "ID_DESPLAZAMIENTO": "1",
            "ORDEN": 2,
            "PERSONAS": {
                "2001": {
                    "MOTVISITA": "3",
                    "MOTVISITA2": "12",
                    "TIPOVISITA": None,
                    "PARENTESCO": ""
                }
            },
            "VISITA": [
                ["1", "1", "2024-05-07"],
                ["2", "1", "Carrera 8"],
                ["3", "1", "3109876543"]
            ]
        }
    ]
}


def _load_fixture(name: str) -> Optional[dict]:
    fpath = FIXTURES_DIR / f"{name}.json"
    if not fpath.exists():
        return None
    with open(fpath) as f:
        return json.load(f)


def _fixture_to_programaciones(fixture_data: dict) -> list[ProgramacionData]:
    prog_list = fixture_data.get("PROGRAMACION", [])
    result = []
    for item in prog_list:
        personas = {}
        for pid, pdata in (item.get("PERSONAS") or {}).items():
            personas[str(pid)] = PersonaRespuesta(
                mot_visita=pdata.get("MOTVISITA") or "",
                mot_visita2=pdata.get("MOTVISITA2") or "",
                tipo_visita=pdata.get("TIPOVISITA"),
                parentesco=pdata.get("PARENTESCO") or "",
                respuestas=pdata.get("RESPUESTAS") or [],
            )

        visita = item.get("VISITA") or []

        prog = ProgramacionData(
            id_programacion=int(item["ID_PROGRAMACION"]),
            estado=item.get("ESTADO", "A"),
            direccion=item.get("DIRECCION", ""),
            otradir=item.get("OTRADIR", ""),
            barrio=item.get("BARRIO", ""),
            id_barrio=item.get("ID_BARRIO"),
            telefono1=item.get("TELEFONO1", ""),
            telefono2=item.get("TELEFONO2", ""),
            latitud=item.get("LATITUD", ""),
            longitud=item.get("LONGITUD", ""),
            dpto=item.get("DPTO", ""),
            municipio=item.get("MUNICIPIO", ""),
            id_desplazamiento=item.get("ID_DESPLAZAMIENTO", ""),
            orden=item.get("ORDEN"),
            personas=personas,
            visita=visita,
        )
        result.append(prog)
    return result


def _decrypt_token(token: str) -> Optional[str]:
    if token and len(token) >= 16:
        return "mock_user"
    return None


@router.api_route(
    "/programacion/get-updates/{token}/{cursor}",
    methods=["GET", "HEAD", "POST"],
)
async def get_updates(
    token: str,
    cursor: str,
    request: Request,
    fixture: Optional[str] = None,
):
    fixture_name = (
        fixture
        or request.headers.get("X-Fixture")
        or request.headers.get("x-fixture")
    )
    is_dev_fixture = fixture_name is not None

    if not is_dev_fixture:
        user = _decrypt_token(token)
        if user is None:
            body = build_error_response(
                f"TOKEN INVALIDO. Action: getUpdates -  Token enviado: {token[:16]}..."
            )
            return JSONResponse(
                content=body,
                status_code=401,
                headers={
                    "Content-Type": "application/json; charset=utf-8",
                    "Expires": "0",
                    "Cache-Control": "must-revalidate, post-check=0, pre-check=0",
                    "Content-Disposition": "inline; filename=Programacion.json; name=Programacion.json",
                },
            )

    fixture_name = (
        fixture
        or request.headers.get("X-Fixture")
        or request.headers.get("x-fixture")
        or "success-default"
    )

    fixture_data = _load_fixture(fixture_name)

    if fixture_data is None:
        fixture_data = SUCCESS_DEFAULT

    if "ERROR" in fixture_data and "PROGRAMACION" not in fixture_data:
        body = build_error_response(fixture_data["ERROR"])
        headers = build_legacy_headers(fecha_sync="")
        return JSONResponse(
            content=body,
            status_code=404,
            headers=headers,
        )

    programaciones = _fixture_to_programaciones(fixture_data)

    body = build_programacion_response(programaciones)
    now_ts = str(int(time.time()))
    cantidad = len(programaciones)

    if fixture_name == "no-fecha-sync":
        headers = build_legacy_headers(fecha_sync="", cantidad_registros=cantidad)
        del headers["FECHA_SYNC"]
    else:
        headers = build_legacy_headers(fecha_sync=now_ts, cantidad_registros=cantidad)

    return JSONResponse(
        content=body,
        status_code=200,
        headers=headers,
    )


@router.get("/health/programacion")
async def health_check():
    return {"status": "ok", "endpoint": "Programacion/getUpdates", "version": "0.1.0"}
