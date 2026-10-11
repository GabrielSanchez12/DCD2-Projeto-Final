import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String, create_engine, event
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

PASTA = Path(__file__).resolve().parent
load_dotenv(PASTA / '.env')
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///assistencia.db')

# O arquivo SQLite fica na pasta do projeto, mesmo ao executar de outra pasta.
if DATABASE_URL == 'sqlite:///assistencia.db':
    DATABASE_URL = f"sqlite:///{(PASTA / 'assistencia.db').as_posix()}"

engine = create_engine(DATABASE_URL)

# No SQLite, a verificação das chaves estrangeiras precisa ser ativada.
if engine.dialect.name == 'sqlite':
    @event.listens_for(engine, 'connect')
    def ativar_chaves_estrangeiras(conexao, registro):
        conexao.execute('PRAGMA foreign_keys=ON')

Session = sessionmaker(bind=engine)
Base = declarative_base()


class Cliente(Base):
    __tablename__ = 'cliente'

    cliente_id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False)
    cidade = Column(String(60), nullable=False)

    reparos = relationship('Reparo', back_populates='cliente')


class Reparo(Base):
    __tablename__ = 'reparo'

    reparo_id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('cliente.cliente_id'), nullable=False)
    tipo_reparo = Column(String(60), nullable=False)
    marca = Column(String(40), nullable=False)
    modelo = Column(String(60), nullable=False)
    data_entrada = Column(Date, nullable=False)
    data_saida = Column(Date, nullable=True)
    valor = Column(Numeric(10, 2), nullable=False)
    status = Column(String(30), nullable=False)

    cliente = relationship('Cliente', back_populates='reparos')
