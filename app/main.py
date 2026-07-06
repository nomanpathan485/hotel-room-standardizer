from fastapi import FastAPI
from app.database import ENGINE
from app.models import Base


Base.metadata.create_all(bind=ENGINE)



app = FastAPI()
@app.get("/")
def root():
    return {"message": "Hotel room standardizer API is running!"}