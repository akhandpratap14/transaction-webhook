from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum


class TransactionStatus(str, Enum):
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class TransactionCreate(BaseModel):
    transaction_id: str = Field(..., example="txn_abc123")
    source_account: str = Field(..., example="acc_user_123")
    destination_account: str = Field(..., example="acc_merchant_456")
    amount: float = Field(..., example=1500.0)
    currency: str = Field(..., example="INR")


class TransactionOut(BaseModel):
    transaction_id: str
    source_account: str
    destination_account: str
    amount: float
    currency: str
    status: TransactionStatus
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
