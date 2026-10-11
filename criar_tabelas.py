from model import Base, engine


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    print('Tabelas cliente e reparo criadas com sucesso!')
