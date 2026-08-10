from decimal import Decimal

from pydantic import BaseModel


class PortfolioXIRR(BaseModel):
    xirr: Decimal
