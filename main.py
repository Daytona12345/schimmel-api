from fastapi import FastAPI
from pydantic import BaseModel
from rechner import schimmel_analyse_kern

app = FastAPI()


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
