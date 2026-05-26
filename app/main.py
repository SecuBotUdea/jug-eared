from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes.alerts import router as alerts_router
from app.api.routes.registry import router as registry_router
from app.api.routes.rescan import router as rescan_router
from app.api.routes.gamification import router as gamification_router
from app.db.repository import connect, disconnect


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect()
    yield
    await disconnect()


app = FastAPI(
    title="jug-eared",
    description="Routing and registry service for the SecuBot-UdeA ecosystem.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(alerts_router)
app.include_router(registry_router)
app.include_router(rescan_router)
app.include_router(gamification_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
