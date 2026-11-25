from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session as OrmSession

import model

app = FastAPI(title='API da Assistência Técnica')


def get_session():
    """Abre uma sessão por requisição e a fecha no final."""
    with model.Session() as session:
        yield session


class ReparoIn(BaseModel):
    cliente_id: int
    tipo_reparo: str = Field(min_length=1, max_length=60)
    marca: str = Field(min_length=1, max_length=40)
    modelo: str = Field(min_length=1, max_length=60)
    data_entrada: date
    data_saida: Optional[date] = None
    valor: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    status: str = Field(min_length=1, max_length=30)


class ReparoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reparo_id: int
    cliente_id: int
    tipo_reparo: str
    marca: str
    modelo: str
    data_entrada: date
    data_saida: Optional[date]
    valor: float
    status: str


@app.get('/reparos', response_model=list[ReparoOut])
def listar_reparos(session: OrmSession = Depends(get_session)):
    return model.listar_reparos(session)


@app.get('/reparos/{reparo_id}', response_model=ReparoOut)
def buscar_reparo(reparo_id: int, session: OrmSession = Depends(get_session)):
    reparo = model.buscar_reparo(session, reparo_id)
    if reparo is None:
        raise HTTPException(status_code=404, detail='Reparo não encontrado')
    return reparo


@app.post('/reparos', response_model=ReparoOut, status_code=201)
def cadastrar_reparo(dados: ReparoIn, session: OrmSession = Depends(get_session)):
    reparo = model.cadastrar_reparo(session, dados.model_dump())
    if reparo is None:
        raise HTTPException(status_code=422, detail='cliente_id não existe')
    return reparo


@app.get('/resumo')
def resumo(session: OrmSession = Depends(get_session)):
    return model.resumir_reparos(session)
