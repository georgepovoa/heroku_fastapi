# start venv  # source venv/bin/activate

from fastapi import FastAPI
from routes.lei import app_routes 
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
CORSMiddleware,
allow_origins=["*"], # Allows all origins
allow_credentials=True,
allow_methods=["*"], # Allows all methods
allow_headers=["*"], # Allows all headers
)

app.include_router(app_routes)

