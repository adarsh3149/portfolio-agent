from fastapi import HTTPException, status

from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository
from app.schemas.asset import AssetCreate


class AssetService:

    def __init__(
        self,
        repository: AssetRepository,
    ):
        self.repository = repository

    def create_asset(
        self,
        request: AssetCreate,
    ) -> Asset:

        existing = self.repository.get_by_symbol(
            request.symbol,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Asset with symbol '{request.symbol}' already exists.",
            )

        asset = Asset(
            symbol=request.symbol,
            name=request.name,
            asset_type=request.asset_type,
            exchange=request.exchange,
            currency=request.currency,
            isin=request.isin,
        )

        return self.repository.create(asset)

    def get_assets(
        self,
    ) -> list[Asset]:

        return self.repository.get_all()

    def get_asset(
        self,
        asset_id: int,
    ) -> Asset:

        asset = self.repository.get_by_id(asset_id)

        if asset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset with ID '{asset_id}' not found.",
            )

        return asset