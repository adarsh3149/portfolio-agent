import hashlib
from decimal import Decimal

from app.schemas.cdsl import CDSLCASTransaction
from app.schemas.portfolio import (
    PortfolioTransaction,
    PortfolioTransactionType,
)


class CDSLTransactionNormalizer:

    SOURCE = "CDSL"

    def normalize(
        self,
        transaction: CDSLCASTransaction,
    ) -> PortfolioTransaction:

        transaction_type = (
            self._resolve_transaction_type(
                transaction.transaction_particulars,
            )
        )

        quantity = self._resolve_quantity(
            transaction,
            transaction_type,
        )

        source_reference = (
            self._build_source_reference(
                transaction,
            )
        )

        return PortfolioTransaction(
            isin=transaction.isin,
            security_name=transaction.security_name,
            transaction_date=transaction.transaction_date,
            transaction_type=transaction_type,
            quantity=quantity,
            source=self.SOURCE,
            source_reference=source_reference,
        )

    def _resolve_transaction_type(
        self,
        particulars: str,
    ) -> PortfolioTransactionType:

        value = particulars.upper().strip()

        if "DIVIDEND" in value:
            return PortfolioTransactionType.DIVIDEND

        if "BONUS" in value:
            return PortfolioTransactionType.BONUS

        if "SPLIT" in value:
            return PortfolioTransactionType.SPLIT

        if "TRANSFER" in value:
            return PortfolioTransactionType.TRANSFER

        if (
            "REDEMPTION" in value
            or "REDEEM" in value
        ):
            return PortfolioTransactionType.REDEMPTION

        if (
            "ALLOTMENT" in value
            or "ALLOT" in value
        ):
            return PortfolioTransactionType.ALLOTMENT

        if (
            "PURCHASE" in value
            or "BUY" in value
        ):
            return PortfolioTransactionType.BUY

        if (
            "SELL" in value
            or "SALE" in value
        ):
            return PortfolioTransactionType.SELL

        return PortfolioTransactionType.OTHER

    def _resolve_quantity(
        self,
        transaction: CDSLCASTransaction,
        transaction_type: PortfolioTransactionType,
    ) -> Decimal:

        if transaction_type in {
            PortfolioTransactionType.REDEMPTION,
            PortfolioTransactionType.SELL,
        }:
            return transaction.debit

        if transaction_type == (
            PortfolioTransactionType.DIVIDEND
        ):
            return transaction.credit

        if transaction.credit > 0:
            return transaction.credit

        if transaction.debit > 0:
            return transaction.debit

        return transaction.credit

    def _build_source_reference(
        self,
        transaction: CDSLCASTransaction,
    ) -> str:

        fingerprint = "|".join(
            [
                transaction.isin,
                transaction.security_name,
                transaction.transaction_date.isoformat(),
                transaction.transaction_particulars,
                str(transaction.opening_balance),
                str(transaction.credit),
                str(transaction.debit),
                str(transaction.closing_balance),
                str(transaction.stamp_duty),
            ]
        )

        digest = hashlib.sha256(
            fingerprint.encode("utf-8")
        ).hexdigest()

        return f"CDSL:{digest}"
