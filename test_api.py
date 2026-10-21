from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api import app, get_session
from model import Base, Cliente, Reparo


@pytest.fixture
def client():
    # Banco em memória: os testes nunca tocam no assistencia.db real.
    engine = create_engine(
        'sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)

    with TestSession() as s:
        s.add(Cliente(cliente_id=1, nome='Ana Silva', telefone='61900000000', cidade='Brasília'))
        s.add(Reparo(
            reparo_id=1, cliente_id=1, tipo_reparo='Troca de tela', marca='Samsung',
            modelo='Galaxy A54', data_entrada=date(2026, 8, 1),
            valor=Decimal('450.00'), status='Em andamento',
        ))
        s.commit()

    def sessao_de_teste():
        with TestSession() as s:
            yield s

    app.dependency_overrides[get_session] = sessao_de_teste
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_listar_e_buscar_reparo(client):
    lista = client.get('/reparos')
    assert lista.status_code == 200
    assert len(lista.json()) == 1

    um = client.get('/reparos/1')
    assert um.status_code == 200
    assert um.json()['modelo'] == 'Galaxy A54'
    assert um.json()['valor'] == 450.0


def test_reparo_inexistente_retorna_404(client):
    resposta = client.get('/reparos/999')
    assert resposta.status_code == 404


def test_cadastrar_reparo_e_resumo(client):
    novo = {
        'cliente_id': 1, 'tipo_reparo': 'Troca de bateria', 'marca': 'Apple',
        'modelo': 'iPhone 12', 'data_entrada': '2026-09-10', 'valor': '200.00',
        'status': 'Em andamento',
    }
    criado = client.post('/reparos', json=novo)
    assert criado.status_code == 201
    assert criado.json()['reparo_id'] == 2
    assert client.get('/reparos/2').json()['marca'] == 'Apple'

    resumo = client.get('/resumo').json()
    assert resumo['total_reparos'] == 2
    assert resumo['valor_total'] == 650.0
    assert resumo['valor_medio'] == 325.0
