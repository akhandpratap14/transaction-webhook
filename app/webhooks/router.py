# app/webhooks/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.database import get_async_session
from app.webhooks import schema, services
import logging

logger = logging.getLogger(__name__)

webhook_router = APIRouter(prefix="/v1/webhooks", tags=["Webhooks"])


@webhook_router.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "message": "Transaction Webhook API is running 🚀"}


@webhook_router.post(
    "/transactions",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Receive transaction webhook",
)
async def receive_transaction_webhook(
    payload: schema.TransactionCreate,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Accepts a webhook payload, stores it, and schedules background processing.
    Includes idempotency check and database error handling.
    """
    try:
        return await services.handle_incoming_webhook(payload, db)

    except IntegrityError:
        # This happens when the same transaction_id is received again
        logger.warning(f"Duplicate transaction received: {payload.transaction_id}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Transaction {payload.transaction_id} already exists",
        )

    except SQLAlchemyError as e:
        logger.error(f"Database error while processing webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while processing transaction.",
        )

    except Exception as e:
        logger.exception(f"Unexpected error in webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while processing webhook.",
        )

@webhook_router.get(
    "/transactions/{transaction_id}",
    response_model=schema.TransactionOut,
    status_code=status.HTTP_200_OK,
    summary="Get transaction details by transaction_id",
)
async def get_transaction_details(
    transaction_id: str,
    db: AsyncSession = Depends(get_async_session),
):
    """
    Fetch transaction details and status by transaction_id.
    Handles not found and database errors gracefully.
    """
    try:
        txn = await services.get_transaction_by_id(transaction_id, db)
        if not txn:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return txn

    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching transaction {transaction_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error while fetching transaction.",
        )

    except Exception as e:
        logger.exception(f"Unexpected error while fetching transaction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error while fetching transaction.",
        )
