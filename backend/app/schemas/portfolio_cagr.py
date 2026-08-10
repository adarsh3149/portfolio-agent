from decimal import Decimal

from pydantic import BaseModel


class PortfolioCAGR(BaseModel):
    cagr: Decimal
