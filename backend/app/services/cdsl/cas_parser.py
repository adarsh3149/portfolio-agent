import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from pypdf import PdfReader

from app.schemas.cdsl import (
    CDSLCASHolding,
    CDSLCASStatement,
)


class CDSLCASParser:

    DATE_PATTERN = re.compile(
        r"Statement\s+for\s+the\s+period\s+from\s+"
        r"(?P<start>\d{2}-[A-Za-z]{3}-\d{4})"
        r"\s+to\s+"
        r"(?P<end>\d{2}-[A-Za-z]{3}-\d{4})",
        re.IGNORECASE,
    )

    ISIN_PATTERN = re.compile(
        r"\b(?P<isin>[A-Z]{2}[A-Z0-9]{10})\b"
    )

    HOLDING_VALUES_PATTERN = re.compile(
        r"""
        (?P<current>\d+(?:\.\d+)?)
        \s+
        --
        \s+
        --
        \s+
        --
        \s+
        (?P<free>\d+(?:\.\d+)?)
        \s+
        (?P<market_price>\d+\.\d{4})
        \s+
        (?P<market_value>[\d,]+\.\d{2})
        """,
        re.VERBOSE,
    )

    PORTFOLIO_VALUE_PATTERN = re.compile(
        r"Portfolio\s+Value\s*[`₹]?\s*"
        r"([\d,]+\.\d{2})",
        re.IGNORECASE,
    )

    def parse(
        self,
        pdf_path: Path,
    ) -> CDSLCASStatement:

        if not pdf_path.exists():
            raise FileNotFoundError(
                pdf_path
            )

        text = self._extract_text(
            pdf_path
        )

        (
            statement_start_date,
            statement_end_date,
        ) = self._parse_statement_period(
            text
        )

        portfolio_value = (
            self._parse_portfolio_value(
                text
            )
        )

        holdings = self._parse_holdings(
            text
        )

        return CDSLCASStatement(
            statement_start_date=(
                statement_start_date
            ),
            statement_end_date=(
                statement_end_date
            ),
            portfolio_value=portfolio_value,
            holdings=holdings,
            transactions=[],
        )

    def _extract_text(
        self,
        pdf_path: Path,
    ) -> str:

        reader = PdfReader(
            str(pdf_path)
        )

        pages: list[str] = []

        for page in reader.pages:
            pages.append(
                page.extract_text() or ""
            )

        return "\n".join(pages)

    def _parse_statement_period(
        self,
        text: str,
    ) -> tuple[date, date]:

        match = self.DATE_PATTERN.search(
            text
        )

        if match is None:
            raise ValueError(
                "Could not find CAS statement period."
            )

        start_date = datetime.strptime(
            match.group("start"),
            "%d-%b-%Y",
        ).date()

        end_date = datetime.strptime(
            match.group("end"),
            "%d-%b-%Y",
        ).date()

        return (
            start_date,
            end_date,
        )

    def _parse_portfolio_value(
        self,
        text: str,
    ) -> Decimal:

        match = (
            self.PORTFOLIO_VALUE_PATTERN.search(
                text
            )
        )

        if match is None:
            raise ValueError(
                "Could not find CAS portfolio value."
            )

        return self._decimal(
            match.group(1)
        )

    def _parse_holdings(
        self,
        text: str,
    ) -> list[CDSLCASHolding]:

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        holdings: list[CDSLCASHolding] = []

        index = 0

        while index < len(lines):

            isin_match = (
                self.ISIN_PATTERN.match(
                    lines[index]
                )
            )

            if isin_match is None:
                index += 1
                continue

            isin = isin_match.group(
                "isin"
            )

            # CDSL extraction can produce either:
            #
            #   INF843K01AO4
            #   EDELWEISS ...
            #
            # or:
            #
            #   INF179KC1FB2 HDFC AMC LTD#...
            #
            # Preserve anything appearing after
            # the ISIN as the beginning of the
            # security name.

            remainder = (
                lines[index][
                    isin_match.end():
                ].strip()
            )

            security_prefix: list[str] = []

            if remainder:
                security_prefix.append(
                    remainder
                )

            (
                holding,
                next_index,
            ) = self._parse_holding_from_lines(
                isin=isin,
                lines=lines,
                start_index=index + 1,
                security_prefix=security_prefix,
            )

            if holding is not None:
                holdings.append(
                    holding
                )

            index = next_index

        return self._deduplicate_holdings(
            holdings
        )

    def _parse_holding_from_lines(
        self,
        isin: str,
        lines: list[str],
        start_index: int,
        security_prefix: list[str] | None = None,
    ) -> tuple[
        CDSLCASHolding | None,
        int,
    ]:

        security_name_parts = list(
            security_prefix or []
        )

        index = start_index

        while index < len(lines):

            line = lines[index]

            # Another ISIN means the current
            # holding could not be completed.
            if self.ISIN_PATTERN.match(
                line
            ):
                break

            if line.startswith(
                "Portfolio Value"
            ):
                break

            match = (
                self.HOLDING_VALUES_PATTERN.search(
                    line
                )
            )

            if match:

                security_name = " ".join(
                    security_name_parts
                ).strip()

                return (
                    CDSLCASHolding(
                        isin=isin,
                        security_name=security_name,
                        units=self._decimal(
                            match.group(
                                "current"
                            )
                        ),
                        market_price=self._decimal(
                            match.group(
                                "market_price"
                            )
                        ),
                        market_value=self._decimal(
                            match.group(
                                "market_value"
                            )
                        ),
                    ),
                    index + 1,
                )

            if not self._is_holding_noise(
                line
            ):
                security_name_parts.append(
                    line
                )

            index += 1

        return (
            None,
            index,
        )

    def _is_holding_noise(
        self,
        line: str,
    ) -> bool:

        noise = (
            "HOLDING STATEMENT",
            "ISIN Security",
            "Current",
            "Frozen",
            "Pledge",
            "Setup",
            "Free Bal",
            "Market Price",
            "Face Value",
            "Value (`)",
            "Statement of Transactions",
            "STATEMENT OF TRANSACTIONS",
            "DP Name",
            "BO ID",
            "Page ",
        )

        return any(
            item.lower() in line.lower()
            for item in noise
        )

    def _decimal(
        self,
        value: str,
    ) -> Decimal:

        return Decimal(
            value.replace(",", "")
        )

    def _deduplicate_holdings(
        self,
        holdings: list[CDSLCASHolding],
    ) -> list[CDSLCASHolding]:

        result: dict[
            str,
            CDSLCASHolding,
        ] = {}

        for holding in holdings:
            result[holding.isin] = holding

        return list(
            result.values()
        )