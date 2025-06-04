"""Cliente HTTP síncrono usando httpx."""

import httpx

from .config import Settings
from .models import KeyInfo, TransferRequest, TransferResult
from .exceptions import PixKeyNotFound, PixTransferError


class PixClient:
    """Facade simples para interação com o servidor Pix (BCB)."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self._http = httpx.Client(
            base_url=self.settings.bcb_base_url,
            timeout=self.settings.timeout,
        )

    # 1. Consulta de chave
    def search_key(self, key: str) -> KeyInfo:
        resp = self._http.get(f"/keys/{key}")
        if resp.status_code == 404:
            raise PixKeyNotFound(key)
        resp.raise_for_status()
        return KeyInfo(**resp.json())

    # 2. Efetua transferência
    def transfer(self, req: TransferRequest) -> TransferResult:
        from dataclasses import asdict
        resp = self._http.post("/transactions", json=asdict(req))
        if resp.status_code >= 400:
            raise PixTransferError(resp.text)
        return TransferResult(**resp.json())
