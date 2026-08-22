from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel


class CDSLTransactionDirection(StrEnum):
    CREDIT = "CREDIT"
    DEBIT = "DEBIT"


class CDSLTransactionEvent(BaseModel):
    security_name: str
    isin: str
    quantity: Decimal
    direction: CDSLTransactionDirection
    transaction_datetime: datetime
    source: str = "CDSL"


@dataclass
class CDSLCASHolding:
    isin: str
    security_name: str
    units: Decimal
    market_price: Decimal
    market_value: Decimal


@dataclass
class CDSLCASTransaction:
    isin: str
    security_name: str
    transaction_particulars: str
    transaction_date: date
    opening_balance: Decimal
    credit: Decimal
    debit: Decimal
    closing_balance: Decimal
    stamp_duty: Decimal


@dataclass
class CDSLCASStatement:
    statement_start_date: date
    statement_end_date: date
    portfolio_value: Decimal
    holdings: list[CDSLCASHolding]
    transactions: list[CDSLCASTransaction]