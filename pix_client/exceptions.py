class PixError(Exception):
    """Exceção base do cliente Pix."""


class PixKeyNotFound(PixError):
    def __init__(self, key: str):
        super().__init__(f"Chave Pix não encontrada: {key}")


class PixTransferError(PixError):
    """Falha na operação de transferência."""

