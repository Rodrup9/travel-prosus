from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import users, groups, trips, itineraries, flights, hotels, votes, group_chat, group_members, ia_chat, auth, websocket_chat
from app.database import init_db, engine
# from app.neo4j_client import Neo4jClient
from app.routers import preferences_neo4j

# neo4j_client = Neo4jClient()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    engine.dispose()
    print("Pool de conexiones cerrado")

app = FastAPI(lifespan=lifespan)

# Incluir routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(groups.router, prefix="/groups", tags=["Groups"])
app.include_router(trips.router, prefix="/trips", tags=["Trips"])
app.include_router(itineraries.router, prefix="/itineraries", tags=["Itineraries"])
app.include_router(flights.router, prefix="/flights", tags=["Flights"])
app.include_router(hotels.router, prefix="/hotels", tags=["Hotels"])
app.include_router(votes.router, prefix="/votes", tags=["Votes"])
app.include_router(group_chat.router, prefix="/group_chat", tags=["Group Chat"])
app.include_router(group_members.router)
app.include_router(ia_chat.router, prefix="/ia_chat", tags=["IA Chat"])
app.include_router(preferences_neo4j.router)
app.include_router(auth.router)
app.include_router(websocket_chat.router, tags=["WebSocket Chat"])


@app.get("/pool-status")
async def pool_status():
    return {
        "pool_size": engine.pool.size(),
        "checked_in": engine.pool.checkedin(),
        "checked_out": engine.pool.checkedout(),
        "overflow": engine.pool.overflow(),
        # "invalid": engine.pool.invalid()
    }