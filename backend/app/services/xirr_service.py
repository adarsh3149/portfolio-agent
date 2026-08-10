from datetime import date
from decimal import Decimal


class XIRRService:

    MAX_ITERATIONS = 100
    TOLERANCE = Decimal("0.0000000001")

    def calculate(
        self,
        cash_flows: list[tuple[date, Decimal]],
    ) -> Decimal:

        if len(cash_flows) < 2:
            raise ValueError(
                "At least two cash flows are required."
            )

        has_positive = any(
            amount > Decimal("0")
            for _, amount in cash_flows
        )

        has_negative = any(
            amount < Decimal("0")
            for _, amount in cash_flows
        )

        if not has_positive or not has_negative:
            raise ValueError(
                "Cash flows must contain both positive and negative values."
            )

        cash_flows = sorted(
            cash_flows,
            key=lambda item: item[0],
        )

        start_date = cash_flows[0][0]

        def npv(rate: Decimal) -> Decimal:
            if rate <= Decimal("-1"):
                raise ValueError(
                    "XIRR rate must be greater than -100%."
                )

            total = Decimal("0")

            for flow_date, amount in cash_flows:
                days = Decimal(
                    (flow_date - start_date).days
                )

                years = days / Decimal("365")

                total += (
                    amount
                    / (
                        (Decimal("1") + rate)
                        ** years
                    )
                )

            return total

        # Find a sign-changing interval.
        lower = Decimal("-0.9999")
        upper = Decimal("1")

        lower_value = npv(lower)
        upper_value = npv(upper)

        while (
            lower_value * upper_value > Decimal("0")
            and upper < Decimal("1000000")
        ):
            upper *= Decimal("2")
            upper_value = npv(upper)

        if lower_value * upper_value > Decimal("0"):
            raise ValueError(
                "Unable to calculate XIRR."
            )

        # Bisection method.
        for _ in range(self.MAX_ITERATIONS):
            midpoint = (
                lower + upper
            ) / Decimal("2")

            midpoint_value = npv(midpoint)

            if abs(midpoint_value) <= self.TOLERANCE:
                return midpoint

            if lower_value * midpoint_value <= Decimal("0"):
                upper = midpoint
                upper_value = midpoint_value
            else:
                lower = midpoint
                lower_value = midpoint_value

        midpoint = (
            lower + upper
        ) / Decimal("2")

        if abs(npv(midpoint)) > Decimal("0.01"):
            raise ValueError(
                "Unable to calculate XIRR."
            )

        return midpoint
