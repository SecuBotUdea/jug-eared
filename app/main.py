from fastapi import FastAPI
from app.api.routes.alerts import router as alerts_router
from app.api.routes.registry import router as registry_router

app = FastAPI(
    title="jug-eared",
    description="Routing and registry service for the SecuBot-UdeA ecosystem.",
    version="0.1.0",
)

app.include_router(alerts_router)
app.include_router(registry_router)


@app.get("/health")
async def health():
    return {"status": "ok"}