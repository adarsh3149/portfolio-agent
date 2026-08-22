from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class CDSLCASDematAccount:
    dp_name: str
    dp_id: str
    client_id: str
    bo_id: str


@dataclass(frozen=True)
class CDSLCASHolding:
    account_bo_id: str
    isin: str
    security_name: str
    current_balance: Decimal
    free_balance: Decimal
    market_price: Decimal
    market_value: Decimal


@dataclass(frozen=True)
class CDSLCASDematTransaction:
    account_bo_id: str
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
    cas_id: str
    period_start: date
    period_end: date
    total_portfolio_value: Decimal

    demat_accounts: list[CDSLCASDematAccount] = field(
        default_factory=list
    )

    holdings: list[CDSLCASHolding] = field(
        default_factory=list
    )

    transactions: list[CDSLCASDematTransaction] = field(
        default_factory=list
    )