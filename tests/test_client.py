# tests/test_client.py
import pytest
import httpx
import json
from pix_client.client import PixClient
from pix_client.config import Settings
from pix_client.models import KeyInfo, TransferRequest, TransferResult
from pix_client.exceptions import PixKeyNotFound, PixTransferError


# -------- utilidade comum --------
def make_client(transport: httpx.MockTransport) -> PixClient:
    """
    Cria um PixClient que usa o MockTransport em vez de abrir conexões reais.
    """
    settings = Settings(bcb_base_url="http://mock", timeout=5.0)
    client = PixClient(settings)
    client._http = httpx.Client(base_url=settings.bcb_base_url, transport=transport)
    return client


def seq_transport(responses):
    """
    Devolve um MockTransport que consome, em ordem, uma lista de
    dicionários com as chaves: method, path, status_code, json|text.
    Serializa o conteúdo JSON antes de devolver.
    """
    def handler(request: httpx.Request):
        assert responses, "foram feitas mais requisições que respostas definidas"
        expected = responses.pop(0)

        # valida método e rota
        assert request.method == expected["method"]
        assert request.url.path == expected["path"]

        # prepara corpo/hdrs
        if "json" in expected:
            content = json.dumps(expected["json"]).encode()
            headers = {"Content-Type": "application/json"}
        else:
            content = expected.get("text", "").encode()
            headers = {"Content-Type": "text/plain"}

        return httpx.Response(
            status_code=expected["status_code"],
            content=content,
            headers=headers,
        )

    return httpx.MockTransport(handler)
# -------- search_key --------
def test_search_key_success():
    key_payload = {"name": "Ausnia", "bank": "Nubank"}
    transport = seq_transport(
        [
            {
                "method": "GET",
                "path": "/search",
                "status_code": 200,
                "json": key_payload,
            }
        ]
    )

    client = make_client(transport)
    info = client.search_key("772384558")

    assert info == KeyInfo(**key_payload)


def test_search_key_not_found():
    transport = seq_transport(
        [
            {
                "method": "GET",
                "path": "/search",
                "status_code": 404,
            }
        ]
    )
    client = make_client(transport)

    with pytest.raises(PixKeyNotFound):
        client.search_key("000000000")


# -------- transfer --------
def test_transfer_success():
    transfer_payload = {
        "recipient": "176086599",
        "sender": "772384558",
        "transaction_id": "abcdef123",
        "value": 1.0,
    }

    transport = seq_transport(
        [
            # 1) valida a chave do destinatário
            {
                "method": "GET",
                "path": "/search",
                "status_code": 200,
                "json": {"name": "Dundîr", "bank": "Bradesco"},
            },
            # 2) realiza a transferência
            {
                "method": "POST",
                "path": "/transfer",
                "status_code": 200,
                "json": transfer_payload,
            },
        ]
    )

    client = make_client(transport)
    req = TransferRequest(sender="772384558", recipient="176086599", value=1)
    result = client.transfer(req)

    assert result == TransferResult(**transfer_payload)


def test_transfer_recipient_not_found():
    transport = seq_transport(
        [
            {
                "method": "GET",
                "path": "/search",
                "status_code": 404,
            }
        ]
    )
    client = make_client(transport)
    req = TransferRequest(sender="772384558", recipient="999999999", value=10)

    with pytest.raises(PixKeyNotFound):
        client.transfer(req)


def test_transfer_server_error():
    transport = seq_transport(
        [
            # Chave válida
            {
                "method": "GET",
                "path": "/search",
                "status_code": 200,
                "json": {"name": "Ausnia", "bank": "Nubank"},
            },
            # Erro ao transferir
            {
                "method": "POST",
                "path": "/transfer",
                "status_code": 500,
                "text": "erro interno",
            },
        ]
    )
    client = make_client(transport)
    req = TransferRequest(sender="772384558", recipient="176086599", value=5)

    with pytest.raises(PixTransferError):
        client.transfer(req)
