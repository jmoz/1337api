from fastapi import FastAPI, Response, status
from pydantic.main import BaseModel

from services.tuned.tuned import get_execution


class Run(BaseModel):
    name: str
    exchange: str
    symbol: str
    timeframe: str
    profit: float
    wins: float
    mdd: float
    trades: int


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/run/{run_id}")
async def run(run_id: str):
    result = await get_execution(run_id)
    if not result:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    item = Run(**result._asdict())
    return item
