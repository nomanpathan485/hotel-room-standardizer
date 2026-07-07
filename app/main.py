from fastapi import FastAPI
from app.database import ENGINE
from app.models import Base
from app.routers import rooms

Base.metadata.create_all(bind=ENGINE)


app = FastAPI()
app.include_router(rooms.router)
@app.get("/")
def root():
    return {"message": "Hotel room standardizer API is running!"}