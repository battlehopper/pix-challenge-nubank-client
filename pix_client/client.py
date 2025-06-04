from dataclasses import asdict
import httpx

from pix_client.config import Settings
from pix_client.exceptions import (
    PixKeyNotFound,
    PixTransferError
)
from pix_client.models import KeyInfo, TransferRequest, TransferResult

class PixClient:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self._http = httpx.Client(
            base_url=self.settings.bcb_base_url,
            timeout=self.settings.timeout,
        )

    # 1. Consulta de chave
    def search_key(self, key: str) -> KeyInfo:
        resp = self._http.get("/search", params={"key": key})
        if resp.status_code == 404:
            raise PixKeyNotFound(key)
        resp.raise_for_status()
        return KeyInfo(**resp.json())

    # 2. Transferência
    def transfer(self, req: TransferRequest) -> TransferResult:
        valid_key = self._http.get("/search", params={"key": req.recipient})
        if valid_key.status_code == 404:
            raise PixKeyNotFound(req.recipient)
        resp = self._http.post("/transfer", json=asdict(req))
        if resp.status_code >= 400:
            raise PixTransferError(resp.text)
        return TransferResult(**resp.json())
