# Pix Client 🏦
Cliente HTTP minimalista, escrito em **Python 3.12**, para integração com o
servidor Pix disponibilizado no desafio _Pix Challenge – IT Engineering Senior
Specialist_ (Nubank).

> ⚠️ Este repositório contém **apenas o service-client**.  
> O servidor mockado do Banco Central (BCB) está no *gist* indicado pelo
> desafio e deve ser clonado/executado separadamente, ou consumido via
> `docker-compose` (veja abaixo).

---

## ✨ Funcionalidades

| # | Descrição |
|---|-----------|
| 1 | **Consulta** de chave Pix: `GET /keys/<pix_key>` |
| 2 | **Transferência** de valores quando a chave existe: `POST /transactions` |
| 3 | **Cliente síncrono** (`httpx`) com time-out configurável |
| 4 | **Configuração via variáveis de ambiente** (`os.getenv`) – sem libs extras |
| 5 | **Modelos/DTOs** em `dataclasses` com type-hints (checados por `mypy`) |
| 6 | **Testes unitários** (`pytest`) com *monkeypatch* de rede |
| 7 | **Dockerfile & Compose** (opcional) para rodar o client + servidor |

---

## 🗂️ Estrutura do projeto

```text
pix_client/
├── pix_client/
│   ├── __init__.py
│   ├── client.py
│   ├── config.py
│   ├── exceptions.py
│   └── models.py
├── tests/
│   ├── test_client.py
│   └── fixtures.json
├── Dockerfile
├── compose.yaml
├── requirements.txt
├── pyproject.toml
├── ASSUMPTIONS.md
└── README.md
```

---

## 🚀 Instalação rápida (local)

```bash
# 1. Ambiente virtual
python -m venv .venv && source .venv/bin/activate

# 2. Dependências de runtime + dev
pip install -r requirements.txt

# 3. (opcional) Execute o servidor mock em outra shell
git clone https://gist.github.com/eltu/7e5cbe533bc7f0e7b93bff7802a5b5de bcb_server
python bcb_server/server.py   # porta 8000 por padrão
```

### Variáveis de ambiente

| Nome | Default | Descrição |
|------|---------|-----------|
| `PIX_BCB_BASE_URL` | `http://localhost:8000` | URL base do servidor Pix |
| `PIX_TIMEOUT`      | `5.0`                   | Time-out em segundos por request |

```bash
export PIX_BCB_BASE_URL=http://bcb-api.internal:8080
```

---

## 🏃 Exemplo de uso (script ad-hoc)

```python
from uuid import uuid4
from pix_client import PixClient
from pix_client.models import TransferRequest

client = PixClient()
info = client.search_key("abc123")
print(f"Chave pertence a {info.account_name} no {info.bank}")

res = client.transfer(
    TransferRequest(
        source_account="001-1234-0",
        destination_key="abc123",
        amount=2_500,          # 25,00 BRL
        idempotency_key=str(uuid4()),
    )
)
print(res)
```

---

## 🐳 Rodando tudo com Docker Compose

```bash
docker compose up --build   # sobe servidor mock + client
```

O serviço *client* apenas inicializa e finaliza (demonstração).  
Edite `compose.yaml` para conectá-lo em modo interativo durante o pair-programming.

---

## ✅ Testes & Qualidade

```bash
pytest -q            # testes unitários
ruff check .         # lint (PEP 8 + opinativas)
mypy pix_client      # type-check
```

Cobertura:

```bash
pytest --cov=pix_client --cov-report=term-missing
```

---

## 🔒 Assumptions-chave

1. Endpoints: `GET /keys/<pix_key>` e `POST /transactions`.  
2. Montantes são inteiros em **centavos**.  
3. Sem TLS/Auth neste protótipo – tema para o pair-programming.

---

## 🌱 Próximas evoluções

1. Retry/back-off e circuit-breaker.  
2. Cache TTL curto para chaves.  
3. Versão assíncrona do cliente.  
4. Release contínuo (wheel + Docker).  
5. mTLS + JWS.

---

## 🤝 Pair-Programming Checklist

| Item | Pronto? |
|------|---------|
| Projeto compila & testes verdes           | ✅ |
| Docker/Compose instalados (unix-like)     | ✅ |
| Script de seed para chaves mockadas       | ✅ |
| Pontos de debate preparados               | ✅ |

---

## 📜 Licença
Uso acadêmico/demonstrativo – nenhuma afiliação ao BCB ou Nubank.

---

> Made with ☕ + 🐍 by **Carlos Brito**
