from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.enums import AssetType
from app.enums import Currency
from app.enums import Exchange


class AssetCreate(BaseModel):
    symbol: str
    name: str

    asset_type: AssetType

    exchange: Exchange

    currency: Currency

    isin: str | None = None


class AssetResponse(BaseModel):
    id: int

    symbol: str
    name: str

    asset_type: AssetType

    exchange: Exchange

    currency: Currency

    isin: str | None

    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class AssetUpdate(BaseModel):
    name: str | None = None

    isin: str | None = None

    is_active: bool | None = None