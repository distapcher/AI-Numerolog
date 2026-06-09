from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from bot.services.numerology_calc import calculate_pythagoras

app = FastAPI(title="Numerology Pythagoras Calc", version="1.0.0")


class BirthDateRequest(BaseModel):
    day: int = Field(ge=1, le=31)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=1900, le=2100)


def _matrix_to_dict(matrix) -> dict[str, Any]:
    return {
        "day": matrix.day,
        "month": matrix.month,
        "year": matrix.year,
        "working_number": matrix.working_number,
        "second_number": matrix.second_number,
        "third_number": matrix.third_number,
        "fourth_number": matrix.fourth_number,
        "digit_counts": matrix.digit_counts,
        "life_path_number": matrix.life_path_number,
        "birth_day_number": matrix.birth_day_number,
        "summary": matrix.format_summary(),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/pythagoras-square")
def pythagoras_square(request: BirthDateRequest) -> dict[str, Any]:
    try:
        matrix = calculate_pythagoras(request.day, request.month, request.year)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "ok", "data": _matrix_to_dict(matrix)}


def run() -> None:
    import uvicorn

    uvicorn.run("calc_service.main:app", host="0.0.0.0", port=8791)


if __name__ == "__main__":
    run()
