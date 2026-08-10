from datetime import date
from decimal import Decimal


class CAGRService:

    def calculate(
        self,
        initial_value: Decimal,
        final_value: Decimal,
        start_date: date,
        end_date: date,
    ) -> Decimal:

        if initial_value <= Decimal("0"):
            raise ValueError(
                "Initial value must be greater than zero."
            )

        if end_date <= start_date:
            raise ValueError(
                "End date must be after start date."
            )

        if final_value < Decimal("0"):
            raise ValueError(
                "Final value cannot be negative."
            )

        if final_value == initial_value:
            return Decimal("0")

        days = Decimal(
            (end_date - start_date).days
        )

        years = (
            days / Decimal("365")
        )

        cagr = (
            (final_value / initial_value)
            ** (Decimal("1") / years)
        ) - Decimal("1")

        return cagr
