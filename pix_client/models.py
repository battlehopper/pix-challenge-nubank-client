from dataclasses import dataclass

@dataclass(slots=True)
class KeyInfo:
    name: str
    bank: str


@dataclass(slots=True)
class TransferRequest:
    sender: str
    recipient: str
    value: float


@dataclass(slots=True)
class TransferResult:
    recipient: str
    sender: str
    transaction_id: str
    value: float
    
