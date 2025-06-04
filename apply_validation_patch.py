#!/usr/bin/env python3
"""
apply_validation_patch.py
-------------------------
Adiciona suporte a validação de formato de chave Pix (InvalidPixKey) e
cria/atualiza arquivos conforme descrito.

Uso:
$ python apply_validation_patch.py
"""
from pathlib import Path
from textwrap import dedent

FILES = {
    "pix_client/exceptions.py": dedent(
        '''
        class PixError(Exception):
            """Exceção base do cliente Pix."""


        class PixKeyNotFound(PixError):
            def __init__(self, key: str):
                super().__init__(f"Chave Pix não encontrada: {key}")


        class PixTransferError(PixError):
            """Falha na operação de transferência."""


        class InvalidPixKey(PixError):
            """Formato da chave Pix é inválido."""
        '''
    ),
    "pix_client/validator.py": dedent(
        '''
        """Validação de formato de chave Pix."""
        import re

        _PATTERNS = {
            "cpf": re.compile(r"^\\d{11}$"),
            "cnpj": re.compile(r"^\\d{14}$"),
            "phone": re.compile(r"^\\+\\d{1,3}\\d{10,11}$"),
            "email": re.compile(r"^[^@]+@[^@]+\\.[^@]+$"),
            "evp": re.compile(r"^[0-9a-f]{32}$"),
        }

        def is_valid_pix_key(key: str) -> bool:
            return any(p.fullmatch(key) for p in _PATTERNS.values())
        '''
    ),
    "pix_client/client.py": dedent(
        '''
        from dataclasses import asdict
        import httpx

        from pix_client.config import Settings
        from pix_client.exceptions import (
            PixKeyNotFound,
            PixTransferError,
            InvalidPixKey,
        )
        from pix_client.models import KeyInfo, TransferRequest, TransferResult
        from pix_client.validator import is_valid_pix_key


        class PixClient:
            def __init__(self, settings: Settings | None = None):
                self.settings = settings or Settings()
                self._http = httpx.Client(
                    base_url=self.settings.bcb_base_url,
                    timeout=self.settings.timeout,
                )

            # 1. Consulta de chave
            def search_key(self, key: str) -> KeyInfo:
                if not is_valid_pix_key(key):
                    raise InvalidPixKey(key)

                resp = self._http.get("/search", params={"key": key})
                if resp.status_code == 404:
                    raise PixKeyNotFound(key)
                resp.raise_for_status()
                return KeyInfo(**resp.json())

            # 2. Transferência
            def transfer(self, req: TransferRequest) -> TransferResult:
                resp = self._http.post("/transfer", json=asdict(req))
                if resp.status_code >= 400:
                    raise PixTransferError(resp.text)
                return TransferResult(**resp.json())
        '''
    ),
    "tests/test_client.py": dedent(
        '''
        import uuid

        import httpx
        import pytest
        from httpx import Request, Response

        from pix_client.client import PixClient
        from pix_client.exceptions import (
            PixKeyNotFound,
            PixTransferError,
            InvalidPixKey,
        )
        from pix_client.models import TransferRequest

        def _stub_get_ok(self, request: Request, **_) -> Response:
            if request.method == "GET" and request.url.path == "/search":
                return Response(
                    200,
                    request=request,
                    json={"name": "Ana", "bank": "Nubank"},
                )
            return Response(500, request=request)

        def _stub_post_ok(self, request: Request, **_) -> Response:
            if request.method == "POST" and request.url.path == "/transfer":
                return Response(
                    201,
                    request=request,
                    json={
                        "recipient": "176086599",
                        "sender": "772384558",
                        "transaction_id": "XYZ",
                        "value": 10.0,
                    },
                )
            return Response(500, request=request)

        def _stub_get_404(self, request: Request, **_) -> Response:
            return Response(404, request=request)

        def _stub_post_500(self, request: Request, **_) -> Response:
            return Response(500, request=request, text="boom")

        # -------------------------- TESTES -------------------------- #
        def test_happy_path(monkeypatch):
            monkeypatch.setattr(httpx.Client, "send", _stub_get_ok)
            client = PixClient()
            info = client.search_key("abc@teste.com")
            assert info.name == "Ana" and info.bank == "Nubank"

            monkeypatch.setattr(httpx.Client, "send", _stub_post_ok)
            result = client.transfer(
                TransferRequest(
                    sender="772384558",
                    recipient="176086599",
                    value=1_000,
                )
            )
            assert result.transaction_id == "XYZ" and result.value == 10.0

        def test_key_not_found(monkeypatch):
            monkeypatch.setattr(httpx.Client, "send", _stub_get_404)
            client = PixClient()
            with pytest.raises(PixKeyNotFound):
                client.search_key("does-not-exist@x.com")

        def test_transfer_failure(monkeypatch):
            monkeypatch.setattr(httpx.Client, "send", _stub_get_ok)
            client = PixClient()
            client.search_key("abc@teste.com")

            monkeypatch.setattr(httpx.Client, "send", _stub_post_500)
            with pytest.raises(PixTransferError):
                client.transfer(
                    TransferRequest(
                        sender="772384558",
                        recipient="176086599",
                        value=1_000,
                    )
                )

        def test_invalid_key_format():
            client = PixClient()
            with pytest.raises(InvalidPixKey):
                client.search_key("123ABC")  # formato inválido
        '''
    ),
}

# -------------------------------------------------------------------

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.lstrip("\n"), encoding="utf-8")
    print(f"✅ {path}")

def main():
    root = Path(".").resolve()
    for rel, txt in FILES.items():
        write_file(root / rel, txt)

    print("\nPatch aplicado. Rode:")
    print("   pytest --cov=pix_client --cov-report=term-missing -q")

if __name__ == "__main__":
    main()
