from fastapi import FastAPI
from src.database import lifespan
from src.routers import router


app = FastAPI(lifespan=lifespan)

# including routers
app.include_router(router)
