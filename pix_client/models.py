from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(slots=True)
class KeyInfo:
    key: str
    account_name: str
    bank: str


@dataclass(slots=True)
class TransferRequest:
    source_account: str
    destination_key: str
    amount: int
    idempotency_key: str


@dataclass(slots=True)
class TransferResult:
    status: Literal["SUCCESS", "FAILURE"]
    created_at: datetime
    tx_id: str
