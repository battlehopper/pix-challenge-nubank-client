# pix_client/cli.py
from __future__ import annotations

import sys
import typer
from rich import print as rprint
from pix_client.client import PixClient
from pix_client.models import TransferRequest
from pix_client.exceptions import PixError


app = typer.Typer(help="Cliente Pix (desafio)")
client = PixClient()


@app.command()                      # type: ignore[misc]
def search(key: str) -> None:       # ← add retorno
    """Consulta uma chave Pix."""
    try:
        info = client.search_key(key)
        rprint(f":white_check_mark:  {info.name} – {info.bank}")
    except PixError as exc:
        rprint(f"[red]{exc}")
        sys.exit(1)


@app.command()                      # type: ignore[misc]
def transfer(sender: str, recipient: str, value: float) -> None:
    """Efetua uma transferência entre duas chaves Pix."""
    try:
        req = TransferRequest(sender=sender, recipient=recipient, value=value)
        result = client.transfer(req)
        rprint(
            f":money_with_wings:  TX {result.transaction_id} – "
            f"{result.sender} → {result.recipient}  R$ {result.value:.2f}"
        )
    except PixError as exc:
        rprint(f"[red]{exc}")
        sys.exit(1)
