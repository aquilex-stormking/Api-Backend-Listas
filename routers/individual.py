from fastapi import APIRouter




router = APIRouter()

@router.get("/individuals")
async def individuals():
    return ["Carlos","Gabriel","Juan"]

