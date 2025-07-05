from fastapi import APIRouter;

router = APIRouter(prefix="/users", tags=["users"]);


@router.get("/")
async def getUsers():
    return [];


    #LcyUBsviY0AI00Td   