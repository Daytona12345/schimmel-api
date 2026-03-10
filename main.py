from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from rechner import schimmel_analyse_kern

app = FastAPI()

# CORS aktivieren (erlaubt Zugriff von deiner Website)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # später besser: ["https://deinedomain.de"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Schimmel API läuft"}


class AnalyseInput(BaseModel):
    t_raum: float
    rF_raum: float
    t_wand: float


@app.post("/calculate")
def calculate(data: AnalyseInput):

    result = schimmel_analyse_kern(
        data.t_raum,
        data.rF_raum,
        data.t_wand
    )

    return result
