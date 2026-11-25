from pathlib import Path

import matplotlib
import pandas as pd
from sqlalchemy import select

from model import PASTA, Reparo, engine

matplotlib.use('Agg')
from matplotlib import pyplot as plt


def analisar_reparos():
    consulta = select(
        Reparo.tipo_reparo, Reparo.valor, Reparo.data_entrada, Reparo.data_saida, Reparo.status
    )
    with engine.connect() as conexao:
        reparos = pd.read_sql(consulta, conexao, parse_dates=['data_entrada', 'data_saida'])

    dias = (reparos['data_saida'] - reparos['data_entrada']).dt.days
    concluidos = reparos['status'].eq('Concluído') & dias.ge(0)
    reparos['dias_conclusao'] = dias.where(concluidos)
    return reparos.groupby('tipo_reparo').agg(
        valor_medio=('valor', 'mean'),
        dias_medios=('dias_conclusao', 'mean'),
    )


def gerar_grafico(resumo, caminho: Path):
    figura, eixos = plt.subplots(1, 2, figsize=(11, 4.5), layout='constrained')
    figura.suptitle('Valor e tempo de conclusão por tipo de reparo')

    for eixo, coluna, titulo, unidade, cor in (
        (eixos[0], 'valor_medio', 'Valor médio', 'R$', '#235a96'),
        (eixos[1], 'dias_medios', 'Tempo médio de conclusão', 'dias', '#27735a'),
    ):
        dados = resumo[coluna].dropna().sort_values()
        eixo.set(title=titulo, xlabel=unidade)
        if dados.empty:
            eixo.text(0.5, 0.5, 'Sem dados disponíveis', ha='center', transform=eixo.transAxes)
            continue
        barras = eixo.barh(dados.index, dados, color=cor)
        rotulos = [f'{valor:.2f}'.replace('.', ',') for valor in dados]
        eixo.bar_label(barras, labels=rotulos, padding=4)
        eixo.margins(x=0.2)

    figura.savefig(caminho, dpi=160)
    plt.close(figura)


def main():
    resumo = analisar_reparos()
    for coluna, titulo, unidade in (
        ('valor_medio', 'Maior valor médio', 'R$'),
        ('dias_medios', 'Maior tempo médio de conclusão', 'dias'),
    ):
        dados = resumo[coluna].dropna()
        if dados.empty:
            print(f'{titulo}: sem dados disponíveis.')
            continue
        maior = dados.max()
        tipos = ', '.join(dados[dados == maior].index)
        valor = f'{maior:.2f}'.replace('.', ',')
        medida = f'R$ {valor}' if unidade == 'R$' else f'{valor} dias'
        print(f'{titulo}: {tipos} ({medida}).')

    caminho = PASTA / 'analise_reparos.png'
    gerar_grafico(resumo, caminho)
    print(f'Gráfico salvo em {caminho}')


if __name__ == '__main__':
    main()
