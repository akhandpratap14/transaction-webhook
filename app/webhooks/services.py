import asyncio
import json
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import async_session_maker
from app import models
from app.webhooks.schema import TransactionCreate, TransactionOut, TransactionStatus
from typing import Optional


async def process_transaction_background(transaction_id: str) -> None:
    await asyncio.sleep(30)

    async with async_session_maker() as session:
        result = await session.execute(
            select(models.Transaction).where(models.Transaction.transaction_id == transaction_id)
        )
        txn = result.scalar_one_or_none()
        if not txn or txn.status == TransactionStatus.PROCESSED:
            return

        txn.status = TransactionStatus.PROCESSED
        txn.processed_at = datetime.utcnow()

        session.add(txn)
        await session.commit()


async def handle_incoming_webhook(payload: TransactionCreate, db: AsyncSession):
    """
    Handles incoming webhook, idempotency check, and background job scheduling.
    """
    result = await db.execute(
        select(models.Transaction).where(models.Transaction.transaction_id == payload.transaction_id)
    )
    existing = result.scalar_one_or_none()

    log = models.WebhookLog(
        transaction_id=payload.transaction_id,
        payload=json.dumps(payload.model_dump())
    )
    db.add(log)

    if existing:
        await db.commit()
        return {"message": "Duplicate webhook received; logged only."}

    txn = models.Transaction(
        transaction_id=payload.transaction_id,
        source_account=payload.source_account,
        destination_account=payload.destination_account,
        amount=payload.amount,
        currency=payload.currency,
        status=TransactionStatus.PROCESSING,
    )
    db.add(txn)

    await db.commit()

    # Background job
    asyncio.get_running_loop().create_task(process_transaction_background(payload.transaction_id))

    return {"message": "Accepted for processing"}

async def get_transaction_by_id(transaction_id: str, db: AsyncSession) -> Optional[TransactionOut]:
    """
    Fetch a transaction by its transaction_id.
    Returns None if not found.
    """
    result = await db.execute(
        select(models.Transaction).where(models.Transaction.transaction_id == transaction_id)
    )
    txn = result.scalar_one_or_none()
    if not txn:
        return None

    return TransactionOut.model_validate(txn)
