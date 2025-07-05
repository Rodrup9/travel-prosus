from fastapi import APIRouter, Depends, HTTPException
from typing import AsyncGenerator
from sqlmodel.ext.asyncio.session import AsyncSession
from uuid import UUID

# Reemplaza esto con tu sesión async real
from app.database import async_session

# TODO: Crear modelo Vote en app/models/vote.py
# Estructura sugerida:
# class Vote(SQLModel, table=True):
#     id: UUID = Field(default_factory=uuid4, primary_key=True)
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     trip_id: UUID = Field(foreign_key="trip.id")
#     user_id: UUID = Field(foreign_key="user.id")
#     vote: bool
#     comment: Optional[str] = None
#     status: bool = True

# Reemplaza esto con tus esquemas reales
# from app.schemas.vote import VoteCreate, VoteRead, VoteUpdate

# Reemplaza esto con tus servicios reales
# from app.services.vote import (
#     create_vote,
#     get_vote,
#     get_all_votes,
#     get_votes_by_trip,
#     get_votes_by_user,
#     update_vote,
#     delete_vote,
# )

router = APIRouter()

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

@router.post("/")  # TODO: Agregar response_model=VoteRead
async def create(data: dict, session: AsyncSession = Depends(get_session)):  # TODO: Cambiar dict por VoteCreate
    """
    Crear un nuevo voto.
    Requiere: trip_id, user_id, vote, comment (opcional)
    """
    # TODO: return await create_vote(session, data)
    raise HTTPException(status_code=501, detail="Implementar create_vote service")

@router.get("/")  # TODO: Agregar response_model=list[VoteRead]
async def read_all(session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los votos.
    """
    # TODO: return await get_all_votes(session)
    raise HTTPException(status_code=501, detail="Implementar get_all_votes service")

@router.get("/trip/{trip_id}")  # TODO: Agregar response_model=list[VoteRead]
async def read_by_trip(trip_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los votos de un viaje específico.
    """
    # TODO: return await get_votes_by_trip(session, trip_id)
    raise HTTPException(status_code=501, detail="Implementar get_votes_by_trip service")

@router.get("/user/{user_id}")  # TODO: Agregar response_model=list[VoteRead]
async def read_by_user(user_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obtener todos los votos de un usuario específico.
    """
    # TODO: return await get_votes_by_user(session, user_id)
    raise HTTPException(status_code=501, detail="Implementar get_votes_by_user service")

@router.get("/{vote_id}")  # TODO: Agregar response_model=VoteRead
async def read(vote_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Obtener un voto específico por ID.
    """
    # TODO: Implementar get_vote service
    # vote = await get_vote(session, vote_id)
    # if not vote:
    #     raise HTTPException(status_code=404, detail="Voto no encontrado")
    # return vote
    raise HTTPException(status_code=501, detail="Implementar get_vote service")

@router.put("/{vote_id}")  # TODO: Agregar response_model=VoteRead
async def update(vote_id: UUID, data: dict, session: AsyncSession = Depends(get_session)):  # TODO: Cambiar dict por VoteUpdate
    """
    Actualizar un voto existente.
    Permite actualizar: vote, comment
    """
    # TODO: Implementar update_vote service
    # vote = await update_vote(session, vote_id, data)
    # if not vote:
    #     raise HTTPException(status_code=404, detail="Voto no encontrado")
    # return vote
    raise HTTPException(status_code=501, detail="Implementar update_vote service")

@router.delete("/{vote_id}")
async def delete(vote_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Eliminar un voto.
    """
    # TODO: Implementar delete_vote service
    # success = await delete_vote(session, vote_id)
    # if not success:
    #     raise HTTPException(status_code=404, detail="Voto no encontrado")
    # return {"ok": True}
    raise HTTPException(status_code=501, detail="Implementar delete_vote service")
