# Backend Flask + Supabase (KidsCare)

API REST para gerenciar clientes, médicos, agendas, atendimentos e pagamentos usando Supabase como camada de persistência.

## Pré-requisitos
- Python 3.10+
- Variáveis de ambiente com as credenciais do projeto Supabase:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY` (recomendado) ou `SUPABASE_ANON_KEY`

Crie um arquivo `.env` na pasta `backend/` ou exporte as variáveis no shell.

## Instalação
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # no Windows use .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Execução
```bash
flask --app app run --debug
```
A API ficará disponível em `http://127.0.0.1:5000`.

## Endpoints principais

### Saúde
- `GET /health` — verificação simples do serviço.

### Clientes
- `GET /api/clientes?status=ativo`
- `POST /api/clientes` — campos obrigatórios: `nome`, `data_nascimento`, `cpf`, `email`, `status`.
- `GET /api/clientes/<id>`
- `PUT /api/clientes/<id>`

### Médicos
- `GET /api/medicos?especialidade=cardio&disponivel=true`
- `POST /api/medicos` — campos obrigatórios: `nome`, `crm`, `especialidade`, `email`, `status`.
- `GET /api/medicos/<id>`
- `PUT /api/medicos/<id>`

### Datas de atendimento
- `GET /api/datas-atendimento?medico_id=1&disponivel=true`
- `POST /api/datas-atendimento` — campos obrigatórios: `medico_id`, `data`, `hora_inicio`, `hora_fim`, `disponivel`, `status`.

### Atendimentos
- `GET /api/atendimentos?cliente_id=1&medico_id=2&status=agendado`
- `POST /api/atendimentos` — campos obrigatórios: `clientes_id`, `medicos_id`, `data_atendimento_id`, `horario`, `tipo_atendimento`, `status`.
- `GET /api/atendimentos/<id>`
- `PUT /api/atendimentos/<id>`

### Pagamentos
- `GET /api/pagamentos?atendimento_id=1&status=pendente`
- `POST /api/pagamentos` — campos obrigatórios: `atendimento_id`, `valor`, `metodo_pagamento`, `status`.
- `PUT /api/pagamentos/<id>`

Todas as rotas retornam erros padronizados no formato `{ "error": "mensagem" }` em caso de falha de validação ou comunicação com o Supabase.
