import argparse
import json
import os
from datetime import datetime, timezone

from bson.json_util import dumps
from pymongo import ASCENDING, MongoClient
from pymongo.errors import PyMongoError

from model import Session, buscar_reparo


def ler_detalhes(texto):
    try:
        detalhes = json.loads(texto)
    except ValueError as erro:
        raise argparse.ArgumentTypeError('Informe um objeto JSON válido.') from erro

    if not isinstance(detalhes, dict):
        raise argparse.ArgumentTypeError('Os detalhes precisam ser um objeto JSON.')
    return detalhes


def main():
    parser = argparse.ArgumentParser(description='Observações técnicas dos reparos no MongoDB')
    acoes = parser.add_subparsers(dest='acao', required=True)
    adicionar = acoes.add_parser('adicionar', help='Registra uma observação técnica')
    adicionar.add_argument('reparo_id', type=int)
    adicionar.add_argument('observacao')
    adicionar.add_argument('--detalhes', type=ler_detalhes, default=None)
    listar = acoes.add_parser('listar', help='Consulta as observações de um reparo')
    listar.add_argument('reparo_id', type=int)
    args = parser.parse_args()

    if args.acao == 'adicionar':
        with Session() as session:
            if buscar_reparo(session, args.reparo_id) is None:
                parser.error(f'Reparo {args.reparo_id} não encontrado no banco relacional.')

    url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    banco = os.getenv('MONGO_DATABASE', 'assistencia')
    try:
        with MongoClient(url, serverSelectionTimeoutMS=5000) as cliente:
            colecao = cliente[banco]['observacoes_reparo']
            filtro = {'reparo_id': args.reparo_id}
            if args.acao == 'adicionar':
                documento = {
                    **filtro,
                    'observacao': args.observacao,
                    'registrado_em': datetime.now(timezone.utc),
                }
                if args.detalhes is not None:
                    documento['detalhes'] = args.detalhes

                colecao.create_index([('reparo_id', ASCENDING), ('registrado_em', ASCENDING)])
                resultado = colecao.insert_one(documento)
                print(f'Observação registrada: {resultado.inserted_id}')
            else:
                observacoes = colecao.find(filtro).sort('registrado_em', ASCENDING)
                print(dumps(list(observacoes), ensure_ascii=False, indent=2))
    except PyMongoError:
        parser.exit(1, 'Erro ao acessar o MongoDB. Confira MONGO_URL e se o serviço está ativo.\n')


if __name__ == '__main__':
    main()
