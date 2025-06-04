# tests/test_client.py
import uuid
import httpx
import pytest
from httpx import Response, Request
from pix_client.client import PixClient
from pix_client.models import TransferRequest
from pix_client.exceptions import PixTransferError
from pix_client.exceptions import PixKeyNotFound


def _fake_send(self, request: Request, **kwargs):
    """Substitui Client.send; devolve Response com o próprio `request` embutido."""
    if request.method == "GET":
        return Response(
            200,
            request=request,
            json={"key": "abc", "account_name": "Ana", "bank": "Nubank"},
        )
    return Response(
        201,
        request=request,
        json={
            "status": "SUCCESS",
            "created_at": "2025-06-01T00:00:00",
            "tx_id": "XYZ",
        },
    )


def test_happy_path(monkeypatch):
    monkeypatch.setattr(httpx.Client, "send", _fake_send)
    client = PixClient()
    client.search_key("abc")
    out = client.transfer(
        TransferRequest("123", "abc", 1000, str(uuid.uuid4()))
    )
    assert out.status == "SUCCESS"

def _fake_404(self, request: Request, **kw):
    return Response(404, request=request)

def test_key_not_found(monkeypatch):
    monkeypatch.setattr(httpx.Client, "send", _fake_404)
    client = PixClient()
    with pytest.raises(PixKeyNotFound):
        client.search_key("xyz")

def _fake_500(self, request: Request, **kw):
    return Response(500, request=request, text="boom")

def test_transfer_failure(monkeypatch):
    monkeypatch.setattr(httpx.Client, "send", _fake_500)
    client = PixClient()
    with pytest.raises(PixTransferError):
        client.transfer(
            TransferRequest("123", "abc", 1000, "idemp")
        )