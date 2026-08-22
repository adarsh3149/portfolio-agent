import re
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from pypdf import PdfReader

from app.schemas.cdsl import CDSLCASTransaction


class CDSLCASNotFoundError(ValueError):
    """Raised when CAS transaction data cannot be found."""


class CDSLCasTransactionParser:

    ISIN_PATTERN = re.compile(
        r"^(?P<isin>[A-Z]{2}[A-Z0-9]{10})(?:\s+(?P<remainder>.*))?$"
    )

    DATE_PATTERN = re.compile(
        r"^(?P<date>\d{2}-\d{2}-\d{4})\s+"
        r"(?P<values>.+)$"
    )

    SETTLEMENT_LINE_PATTERN = re.compile(
        r"^\d{2}\s+\d{8}[A-Z0-9]+$"
    )

    STAMP_DUTY_PATTERN = re.compile(
        r"^(?P<value>\d+(?:\.\d+)?)$"
    )

    def parse(
        self,
        pdf_path: Path,
    ) -> list[CDSLCASTransaction]:

        if not pdf_path.exists():
            raise FileNotFoundError(
                pdf_path
            )

        text = self._extract_text(
            pdf_path
        )

        transaction_text = (
            self._extract_transaction_section(
                text
            )
        )

        transactions = (
            self._parse_transactions(
                transaction_text
            )
        )

        if not transactions:
            raise CDSLCASNotFoundError(
                "No CAS transactions found."
            )

        return transactions

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

    def _extract_transaction_section(
        self,
        text: str,
    ) -> str:

        marker = (
            "STATEMENT OF TRANSACTIONS"
        )

        start = text.find(marker)

        if start == -1:
            raise CDSLCASNotFoundError(
                "CAS transaction section not found."
            )

        return text[start:]

    def _parse_transactions(
        self,
        text: str,
    ) -> list[CDSLCASTransaction]:

        lines = [
            self._clean_line(line)
            for line in text.splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        transactions: list[
            CDSLCASTransaction
        ] = []

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

            remainder = (
                isin_match.group(
                    "remainder"
                )
                or ""
            ).strip()

            security_name, next_index = (
                self._parse_security_name(
                    lines=lines,
                    start_index=index + 1,
                    remainder=remainder,
                )
            )

            (
                security_transactions,
                next_index,
            ) = self._parse_security_transactions(
                isin=isin,
                security_name=security_name,
                lines=lines,
                start_index=next_index,
            )

            transactions.extend(
                security_transactions
            )

            index = next_index

        return transactions

    def _parse_security_name(
        self,
        lines: list[str],
        start_index: int,
        remainder: str,
    ) -> tuple[str, int]:

        security_parts: list[str] = []

        if remainder:
            security_parts.append(
                remainder
            )

        index = start_index

        while index < len(lines):

            line = lines[index]

            if self._is_transaction_particular_line(
                line
            ):
                break

            if self._is_transaction_date_line(
                line
            ):
                break

            if self.ISIN_PATTERN.match(
                line
            ):
                break

            if self._is_page_or_header(
                line
            ):
                index += 1
                continue

            security_parts.append(
                line
            )

            index += 1

        return (
            " ".join(security_parts).strip(),
            index,
        )

    def _parse_security_transactions(
        self,
        isin: str,
        security_name: str,
        lines: list[str],
        start_index: int,
    ) -> tuple[
        list[CDSLCASTransaction],
        int,
    ]:

        transactions: list[
            CDSLCASTransaction
        ] = []

        index = start_index

        particulars_parts: list[str] = []

        while index < len(lines):

            line = lines[index]

            # New security.
            if (
                self.ISIN_PATTERN.match(
                    line
                )
            ):
                break

            # End of this transaction section.
            if self._is_page_or_header(
                line
            ):
                index += 1
                continue

            # Transaction particulars.
            if self._is_transaction_particular_line(
                line
            ):
                particulars_parts.append(
                    line
                )
                index += 1
                continue

            date_match = (
                self.DATE_PATTERN.match(
                    line
                )
            )

            if date_match:

                transaction = (
                    self._build_transaction(
                        isin=isin,
                        security_name=security_name,
                        particulars=" ".join(
                            particulars_parts
                        ),
                        date_value=(
                            date_match.group(
                                "date"
                            )
                        ),
                        values=(
                            date_match.group(
                                "values"
                            )
                        ),
                    )
                )

                if transaction is not None:
                    transactions.append(
                        transaction
                    )

                particulars_parts = []

                index += 1
                continue

            index += 1

        return (
            transactions,
            index,
        )

    def _build_transaction(
        self,
        isin: str,
        security_name: str,
        particulars: str,
        date_value: str,
        values: str,
    ) -> CDSLCASTransaction | None:

        tokens = values.split()

        if len(tokens) < 4:
            return None

        # CAS extraction has two formats:
        #
        # First row:
        #   OpBal Credit Debit ClBal Stamp
        #
        # Subsequent rows:
        #   Credit Debit ClBal Stamp
        #
        # Examples:
        #
        # 85.907 0.790 -- 86.697 0
        #
        # 0.788 -- 87.485 0
        #
        # Therefore infer the format from
        # the number of tokens.

        if len(tokens) == 5:

            opening_balance = (
                self._decimal(tokens[0])
            )

            credit = self._decimal_or_zero(
                tokens[1]
            )

            debit = self._decimal_or_zero(
                tokens[2]
            )

            closing_balance = (
                self._decimal(tokens[3])
            )

            stamp_duty = (
                self._decimal(tokens[4])
            )

        elif len(tokens) == 4:

            opening_balance = Decimal(
                "0"
            )

            credit = self._decimal_or_zero(
                tokens[0]
            )

            debit = self._decimal_or_zero(
                tokens[1]
            )

            closing_balance = (
                self._decimal(tokens[2])
            )

            stamp_duty = (
                self._decimal(tokens[3])
            )

        else:
            return None

        return CDSLCASTransaction(
            isin=isin,
            security_name=security_name,
            transaction_particulars=(
                particulars
            ),
            transaction_date=(
                datetime.strptime(
                    date_value,
                    "%d-%m-%Y",
                ).date()
            ),
            opening_balance=opening_balance,
            credit=credit,
            debit=debit,
            closing_balance=closing_balance,
            stamp_duty=stamp_duty,
        )

    def _is_transaction_particular_line(
        self,
        line: str,
    ) -> bool:

        if line.startswith(
            "SETT "
        ):
            return True

        return bool(
            self.SETTLEMENT_LINE_PATTERN.match(
                line
            )
        )

    def _is_transaction_date_line(
        self,
        line: str,
    ) -> bool:

        return bool(
            self.DATE_PATTERN.match(
                line
            )
        )

    def _is_page_or_header(
        self,
        line: str,
    ) -> bool:

        ignored = (
            "ISIN Security",
            "ISINISIN",
            "Transaction Particulars",
            "Transaction",
            "Particulars",
            "Op. Bal",
            "Credit",
            "Debit",
            "Cl. Bal",
            "Stamp Duty",
            "Page ",
            "STATEMENT OF TRANSACTIONS",
        )

        return any(
            line.startswith(
                value
            )
            for value in ignored
        )

    def _clean_line(
        self,
        line: str,
    ) -> str:

        return (
            line
            .replace("\u00ad", "")
            .replace("\ufffd", "-")
            .strip()
        )

    def _decimal(
        self,
        value: str,
    ) -> Decimal:

        return Decimal(
            value.replace(",", "")
        )

    def _decimal_or_zero(
        self,
        value: str,
    ) -> Decimal:

        if value == "--":
            return Decimal("0")

        return self._decimal(
            value
        )