"""Leitura simples de variáveis de ambiente usando apenas stdlib."""

from dataclasses import dataclass
import os


@dataclass(slots=True)
class Settings:
    """Configuração do cliente Pix.

    Variáveis de ambiente:
    - PIX_BCB_BASE_URL: URL base do servidor Pix (default http://127.0.0.1:5000)
    - PIX_TIMEOUT:      Timeout em segundos (default 5.0)
    """

    bcb_base_url: str = os.getenv("PIX_BCB_BASE_URL", "http://127.0.0.1:5000")
    timeout: float = float(os.getenv("PIX_TIMEOUT", "5.0"))
