from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    Enum,
    func,
    UniqueConstraint,
)
from app.database import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid
import enum

class TransactionStatus(str, enum.Enum):
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"

class Transaction(BaseModel):
    """
    Represents a single transaction webhook event.
    """
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    transaction_id = Column(String(255), unique=True, nullable=False)
    source_account = Column(String(255), nullable=False)
    destination_account = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PROCESSING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("transaction_id", name="uq_transaction_id"),
    )

    def __repr__(self):
        return f"<Transaction(transaction_id={self.transaction_id}, status={self.status})>"


class WebhookLog(BaseModel):
    """
    Optional table for debugging or future analytics — tracks raw webhook payloads.
    Useful when testing multiple webhook retries.
    """
    __tablename__ = "webhook_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    transaction_id = Column(String(255), index=True, nullable=False)
    payload = Column(String, nullable=True)  # store JSON payload as string if needed
    received_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<WebhookLog(transaction_id={self.transaction_id})>"
