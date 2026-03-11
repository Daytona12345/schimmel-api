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

class Punkt(BaseModel):
    name: str
    temp: float

class AnalyseInput(BaseModel):
    mode: str | None = None
    t_raum: float
    rF_raum: float
    t_wand: float | None = None
    punkte: list[Punkt] | None = None

@app.post("/calculate")
def calculate(data: AnalyseInput):

    # Fall 1: klassische Einzelmessung
    if data.t_wand is not None:
        result = schimmel_analyse_kern(
            data.t_raum,
            data.rF_raum,
            data.t_wand
        )
        return result

    # Fall 2: Mehrpunktmessung (UI 4.1)
    if data.punkte:

        results = []

        for p in data.punkte:
            r = schimmel_analyse_kern(
                data.t_raum,
                data.rF_raum,
                p.temp
            )

            results.append({
                "punkt": p.name,
                "temp": p.temp,
                "analyse": r
            })

        return {
            "punkte": results
        }

    return {"error": "Keine Messwerte übergeben"}
