from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from rechner import schimmel_analyse_kern
from textbausteine import get_textbausteine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

    # Einzelmessung
    if data.t_wand is not None:

        r = schimmel_analyse_kern(
            data.t_raum,
            data.rF_raum,
            data.t_wand
        )

        return {
            "taupunkt":         r["taupunkt"],
            "taupunkt_abstand": r["taupunkt_abstand"],
            "surfRH":           r["surfRH"],
            "delta_t":          r["delta_t"],
            "scenario_id":      r["scenario_id"],
            "ursache":          r["ursache"],
            "befund1":          r["befund1"],
            "befund2":          r["befund2"],
            "befund3":          r["befund3"],
        }

    # Mehrpunktmessung
    if data.punkte:

        results = []

        for p in data.punkte:

            r = schimmel_analyse_kern(
                data.t_raum,
                data.rF_raum,
                p.temp
            )

            results.append({
                "punkt":   p.name,
                "temp":    p.temp,
                "analyse": r,
            })

        return {
            "punkte": results
        }

    return {"error": "Keine Messwerte übergeben"}
