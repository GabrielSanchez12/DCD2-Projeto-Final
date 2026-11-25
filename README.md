# Assistência Técnica de Celulares

O sistema registra clientes e reparos de celulares. O PostgreSQL armazena as tabelas `cliente` e `reparo`, ligadas por `cliente_id`. A API usa FastAPI e acessa o banco por meio do Model com SQLAlchemy.

## Como rodar

Instale o Python 3.10 ou superior, inicie o PostgreSQL e crie um banco vazio chamado `assistencia`. No pgAdmin, abra o Query Tool conectado ao banco `postgres` e execute `CREATE DATABASE assistencia;`. O usuário configurado para o projeto precisa ter permissão para criar tabelas nesse banco.

No PowerShell, na pasta do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.exemplo .env
```

No Linux ou macOS, use `python3 -m venv .venv`, `source .venv/bin/activate` e `cp .env.exemplo .env` para as etapas equivalentes.

No arquivo local `.env`, ajuste `DATABASE_URL` para usar o usuário, a senha, o host e a porta do seu PostgreSQL. Use o formato `postgresql+psycopg://usuario:senha@localhost:5432/assistencia`. Se a senha contiver caracteres especiais de URL, codifique esses caracteres na URL.

```text
python criar_tabelas.py
python popular.py
python -m pytest -q
python analise.py
python -m uvicorn api:app
```

Abra [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) para experimentar as quatro rotas da API:

| Método e rota | Ação |
| --- | --- |
| `GET /reparos` | Lista os reparos. |
| `GET /reparos/{reparo_id}` | Busca um reparo pelo ID. |
| `POST /reparos` | Cadastra um reparo de um cliente existente. |
| `GET /resumo` | Mostra a quantidade, a soma dos valores, o valor médio e as contagens por status. |

## Análise

> Qual tipo de reparo apresenta maior valor médio e maior tempo de conclusão?

Nos dados de exemplo, **reparo na placa** tem o maior valor médio, **R$ 616,00**, e **troca de tela** tem o maior tempo médio de conclusão, **4,25 dias**. Os dois indicadores apontam para tipos diferentes de reparo.

O script `analise.py` lê os reparos do PostgreSQL e usa Pandas para calcular o valor médio por tipo a partir dos 20 registros. Para calcular o tempo médio, usa os 16 reparos concluídos com datas válidas e mede a diferença entre a data de saída e a data de entrada. O Matplotlib salva o gráfico em `analise_reparos.png`. O gráfico abaixo usa os dados de exemplo.

![Gráficos de valor médio e tempo médio de conclusão por tipo de reparo](analise_reparos.png)

## Item à escolha — MongoDB

Escolhemos o MongoDB para guardar observações dos técnicos porque o conteúdo varia conforme o defeito. Um documento pode registrar apenas uma descrição, enquanto outro pode incluir a peça inspecionada, medições ou uma lista de testes. Cada documento mantém o ID do reparo correspondente no PostgreSQL. O processamento paralelo teria pouco benefício para a carga atual, que usa 20 reparos de exemplo em consultas e agregações curtas.

Para usar o módulo, inicie o MongoDB e confira `MONGO_URL` e `MONGO_DATABASE` no `.env`. Com o PostgreSQL já populado, execute:

```text
python mongo_observacoes.py adicionar 1 "Tela sem resposta ao toque durante o teste."
python mongo_observacoes.py listar 1
```

Na opção `adicionar`, o argumento `--detalhes` aceita um objeto JSON com campos adicionais. O script verifica se o ID existe no PostgreSQL antes de gravar a observação na coleção `observacoes_reparo`.
