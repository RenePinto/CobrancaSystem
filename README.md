# CobrancaSystem
Desenvolvimento de sistema para auxílio de cobrança.

## Visão geral
Backend em FastAPI para consolidação e envio de cobranças vencidas com:
- Autenticação JWT (admin e operadora)
- 2FA via TOTP
- Upload de planilhas Itaú e Conta Azul (.xlsx)
- Normalização e deduplicação de dados
- Persistência em PostgreSQL
- Snapshots de relatórios e histórico de envios

## Estrutura de pastas
```
app/
  core/            # Config, segurança, banco e dependências
  models/          # ORM SQLAlchemy
  schemas/         # Schemas Pydantic
  repositories/    # Acesso a dados
  services/        # Regras de negócio
  routers/         # Endpoints REST
  utils/           # Utilitários (parsers Excel)
  main.py          # Aplicação FastAPI
```

## Como rodar com Docker
```bash
docker compose up --build
```
A API ficará disponível em `http://localhost:8000`.

## Deploy no Render
Se você usa o Render diretamente (sem Docker), configure o serviço com:

- **Build Command:** `pip install --upgrade pip setuptools wheel && pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Python version:** `3.11.9` (definido via `runtime.txt`)
- **DATABASE_URL:** defina a string de conexão do Postgres no painel do Render (ex.: `postgresql+psycopg2://user:pass@host:5432/db`). Sem isso, a aplicação tenta usar `db` como host (padrão do Docker Compose) e falha com `could not translate host name "db"`.

Essas configurações garantem que o Render instale wheels pré-compilados do `pandas` e evite o erro `metadata-generation-failed`.

> **Importante:** remova qualquer linha `pythonVersion` de um `render.yaml` antigo. Esse campo não é aceito pelo schema atual do Render Blueprint e causa o erro `"field pythonVersion not found in type file.Service"`.

## Configuração inicial
Crie um usuário admin usando o endpoint `/users` (exige token). Para o primeiro acesso, você pode inserir manualmente um admin no banco ou usar o shell dentro do container para criar um usuário via script. O fluxo recomendado é:
1. Iniciar o container.
2. Inserir o usuário admin diretamente na tabela `users`.
3. Autenticar e criar usuários via API.

## Regras de normalização
- Somente vencidos: `data_vencimento < hoje`
- Valor > 0
- `cliente`, `descricao` e `vendedor` obrigatórios
- Deduplicação por `(cliente, data_vencimento, valor_original, descricao, origem)`

## Endpoints principais
- `POST /auth/login` - autenticação JWT
- `POST /auth/setup-2fa` - gera segredo TOTP
- `POST /auth/verify-2fa` - habilita 2FA
- `POST /users` - cria usuários (admin)
- `POST /invoices/upload/itau` - upload Itaú
- `POST /invoices/upload/conta-azul` - upload Conta Azul
- `POST /reports/snapshot` - gera snapshot e histórico
- `GET /history` - lista histórico de envios

## Exemplos de requests/responses
### Login
**Request**
```json
POST /auth/login
{
  "username": "admin",
  "password": "secret",
  "totp_code": "123456"
}
```
**Response**
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

### Upload Itaú
**Request**
```
POST /invoices/upload/itau
Content-Type: multipart/form-data
file=@/caminho/itau.xlsx
```
**Response**
```json
{
  "inserted": 120,
  "skipped_invalid": 5,
  "skipped_duplicates": 12
}
```

### Gerar snapshot de relatório
**Request**
```json
POST /reports/snapshot
{
  "report_type": "vencidos",
  "recipient_type": "DIRETORIA",
  "method": "EXPORT",
  "recipient_value": "Diretoria"
}
```
**Response**
```json
{
  "id": 10,
  "report_type": "vencidos",
  "recipient_type": "DIRETORIA",
  "method": "EXPORT",
  "created_at": "2024-03-10T12:00:00Z",
  "data_json": [
    {
      "cliente": "Empresa X",
      "data_vencimento": "2024-03-01",
      "descricao": "Mensalidade",
      "valor_original": 1200.5,
      "vendedor": "João",
      "origem": "ITAU"
    }
  ]
}
```

### Histórico de envios
**Request**
```
GET /history
```
**Response**
```json
[
  {
    "id": 1,
    "recipient_type": "DIRETORIA",
    "recipient_value": "Diretoria",
    "report_type": "vencidos",
    "method": "EXPORT",
    "sent_at": "2024-03-10T12:00:00Z",
    "snapshot_id": 10
  }
]
```

## Documentação OpenAPI
Acesse `http://localhost:8000/docs` para visualizar a documentação interativa.
