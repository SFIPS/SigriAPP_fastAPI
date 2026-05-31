import time
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

import ibm_db
from database import get_connection
from models.programacion import (
    ProgramacionData,
    PersonaRespuesta,
    build_programacion_response,
    build_error_response,
    build_legacy_headers,
)

router = APIRouter()

SCHEMA = "SALUD"


def _query_all(sql: str, params: list = None) -> list[dict]:
    conn = get_connection()
    try:
        stmt = ibm_db.prepare(conn, sql)
        if params:
            ibm_db.execute(stmt, params)
        else:
            ibm_db.execute(stmt)
        rows = []
        row = ibm_db.fetch_assoc(stmt)
        while row:
            rows.append(dict(row))
            row = ibm_db.fetch_assoc(stmt)
        return rows
    finally:
        ibm_db.close(conn)


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
):
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

    body_raw = await request.body()
    client_ids = []
    if body_raw:
        import json
        client_ids = json.loads(body_raw)

    rows = _query_all(
        f"SELECT * FROM {SCHEMA}.SF_PROGRAMACION WHERE ESTADO IN ('A', 'D', 'PR') ORDER BY ID_PROGRAMACION"
    )

    if not rows:
        body = build_error_response("NO HAY RESULTADOS")
        return JSONResponse(
            content=body,
            status_code=404,
            headers=build_legacy_headers(fecha_sync=""),
        )

    programaciones = []
    for row in rows:
        id_prog = int(row["ID_PROGRAMACION"])
        if id_prog in client_ids:
            continue

        det_rows = _query_all(
            f"SELECT * FROM {SCHEMA}.SF_PROGRAMACION_DET WHERE ID_PROGRAMACION = ?",
            [id_prog],
        )

        personas = {}
        for det in det_rows:
            pid = str(det["ID_USUARIO"])
            personas[pid] = PersonaRespuesta(
                mot_visita=(det.get("MOTVISITA") or "").strip(),
                mot_visita2="",
                tipo_visita=(det.get("TIPOVISITA") or "").strip() or None,
                parentesco=(det.get("PARENTESCO") or "").strip(),
            )

        prog = ProgramacionData(
            id_programacion=id_prog,
            estado=(row.get("ESTADO") or "A").strip(),
            direccion=(row.get("DIRECCION") or "").strip(),
            otradir=(row.get("OTRADIR") or "").strip(),
            barrio=(row.get("BARRIO") or "").strip(),
            id_barrio=int(row["ID_BARRIO"]) if row.get("ID_BARRIO") is not None else None,
            telefono1=(row.get("TELEFONO1") or "").strip(),
            telefono2=(row.get("TELEFONO2") or "").strip(),
            latitud=(row.get("LATITUD") or "").strip(),
            longitud=(row.get("LONGITUD") or "").strip(),
            dpto=(row.get("DPTO") or "").strip(),
            municipio=(row.get("MUNICIPIO") or "").strip(),
            id_desplazamiento=str(row.get("ID_DESPLAZAMIENTO") or "").strip(),
            orden=None,
            personas=personas,
            visita=[],
        )
        programaciones.append(prog)

    if not programaciones:
        body = build_error_response("NO HAY RESULTADOS")
        return JSONResponse(
            content=body,
            status_code=404,
            headers=build_legacy_headers(fecha_sync=""),
        )

    body = build_programacion_response(programaciones)
    now_ts = str(int(time.time()))
    headers = build_legacy_headers(
        fecha_sync=now_ts,
        cantidad_registros=len(programaciones),
    )

    return JSONResponse(
        content=body,
        status_code=200,
        headers=headers,
    )


@router.get("/health/programacion")
async def health_check():
    return {"status": "ok", "endpoint": "Programacion/getUpdates", "version": "0.2.0"}
