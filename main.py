# start venv  # source venv/bin/activate

from fastapi import FastAPI
from routes.lei import app_routes 
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8000/lei",
    "http://127.0.0.1:8000/lei/0",
    "http://localhost:8000/imagem-cortada"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app_routes)

