from datetime import date, timedelta
from decimal import Decimal

from model import Cliente, Reparo, Session


if __name__ == '__main__':
    with Session() as session:
        # Evita duplicar os exemplos quando este script for executado novamente.
        if session.query(Cliente).first() or session.query(Reparo).first():
            print('O banco já possui dados. Nenhum exemplo foi inserido.')
        else:
            nomes = [
                'Ana Silva', 'Bruno Souza', 'Carla Lima', 'Diego Santos',
                'Eduarda Costa', 'Felipe Alves', 'Gabriela Rocha',
                'Henrique Melo', 'Isabela Dias', 'João Martins',
            ]
            cidades = ['Brasília', 'Taguatinga', 'Ceilândia', 'Guará', 'Sobradinho']
            clientes = []
            for i, nome in enumerate(nomes):
                cliente = Cliente(
                    nome=nome,
                    telefone=f'6190000{i:04d}',  # Telefones fictícios.
                    cidade=cidades[i % len(cidades)],
                )
                clientes.append(cliente)
                session.add(cliente)

            session.flush()  # Gera os IDs dos clientes antes de cadastrar os reparos.

            tipos = ['Troca de tela', 'Troca de bateria', 'Reparo no conector', 'Reparo na placa']
            aparelhos = [('Samsung', 'Galaxy A54'), ('Apple', 'iPhone 12'),
                         ('Motorola', 'Moto G84'), ('Xiaomi', 'Redmi Note 12')]
            valores = ['450.00', '180.00', '150.00', '600.00']

            for i in range(20):
                entrada = date(2026, 8, 1) + timedelta(days=i * 3)
                concluido = i < 16
                marca, modelo = aparelhos[i % 4]
                reparo = Reparo(
                    cliente_id=clientes[i % 10].cliente_id,
                    tipo_reparo=tipos[i % 4],
                    marca=marca,
                    modelo=modelo,
                    data_entrada=entrada,
                    data_saida=entrada + timedelta(days=2 + i % 5) if concluido else None,
                    valor=Decimal(valores[i % 4]) + Decimal(i % 3) * Decimal('20.00'),
                    status='Concluído' if concluido else 'Em andamento',
                )
                session.add(reparo)

            session.commit()
            print('10 clientes e 20 reparos cadastrados com sucesso!')
