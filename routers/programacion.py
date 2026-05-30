from fastapi import APIRouter

router = APIRouter()


@router.post("/programacion/get-updates/{token}/{cursor}")
async def get_updates(token: str, cursor: str):
    return {"message": "not implemented yet"}
