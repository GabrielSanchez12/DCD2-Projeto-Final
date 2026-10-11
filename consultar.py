from model import Cliente, Reparo, Session


if __name__ == '__main__':
    with Session() as session:
        print(f'Total de clientes: {session.query(Cliente).count()}')
        print(f'Total de reparos: {session.query(Reparo).count()}')
        print('\nPrimeiros 5 reparos (com o nome do cliente):')
        reparos = session.query(Reparo).order_by(Reparo.reparo_id).limit(5).all()
        for reparo in reparos:
            print(
                f'{reparo.reparo_id} | {reparo.cliente.nome} | '
                f'{reparo.tipo_reparo} | R$ {reparo.valor:.2f} | {reparo.status}'
            )
