from datetime import datetime
from decimal import Decimal

from bs4 import BeautifulSoup

from app.schemas.cdsl import (
    CDSLTransactionDirection,
    CDSLTransactionEvent,
)


class CDSLDailyEmailParser:

    REQUIRED_HEADERS = {
        "company name",
        "isin",
        "quantity",
        "debit / credit",
        "date and time",
    }

    def parse(
        self,
        email_body: str,
    ) -> list[CDSLTransactionEvent]:

        soup = BeautifulSoup(
            email_body,
            "html.parser",
        )

        for table in soup.find_all("table"):

            rows = table.find_all("tr")

            header_index = self._find_header_row(
                rows,
            )

            if header_index is None:
                continue

            headers = self._get_headers(
                rows[header_index],
            )

            events: list[CDSLTransactionEvent] = []

            for row in rows[header_index + 1:]:
                event = self._parse_row(
                    row,
                    headers,
                )

                if event is not None:
                    events.append(event)

            return events

        return []

    def _find_header_row(
        self,
        rows,
    ) -> int | None:

        for index, row in enumerate(rows):

            cells = row.find_all(
                ["th", "td"],
            )

            headers = {
                cell.get_text(
                    " ",
                    strip=True,
                ).lower()
                for cell in cells
            }

            if self.REQUIRED_HEADERS.issubset(
                headers,
            ):
                return index

        return None

    @staticmethod
    def _get_headers(
        row,
    ) -> dict[str, int]:

        headers: dict[str, int] = {}

        cells = row.find_all(
            ["th", "td"],
        )

        for index, cell in enumerate(cells):

            header = cell.get_text(
                " ",
                strip=True,
            ).lower()

            headers[header] = index

        return headers

    def _parse_row(
        self,
        row,
        headers: dict[str, int],
    ) -> CDSLTransactionEvent | None:

        cells = row.find_all("td")

        if not cells:
            return None

        values = [
            cell.get_text(
                " ",
                strip=True,
            )
            for cell in cells
        ]

        required_indexes = [
            headers["company name"],
            headers["isin"],
            headers["quantity"],
            headers["debit / credit"],
            headers["date and time"],
        ]

        if any(
            index >= len(values)
            for index in required_indexes
        ):
            return None

        security_name = values[
            headers["company name"]
        ].strip()

        isin = values[
            headers["isin"]
        ].strip().upper()

        quantity_text = values[
            headers["quantity"]
        ].strip()

        direction_text = values[
            headers["debit / credit"]
        ].strip().upper()

        datetime_text = values[
            headers["date and time"]
        ].strip()

        if not security_name or not isin:
            return None

        try:
            quantity = Decimal(
                quantity_text,
            )

            transaction_datetime = datetime.strptime(
                datetime_text,
                "%d/%m/%Y %H:%M:%S",
            )

        except (
            ValueError,
            ArithmeticError,
        ):
            return None

        if direction_text == "CREDIT":

            direction = (
                CDSLTransactionDirection.CREDIT
            )

        elif direction_text == "DEBIT":

            direction = (
                CDSLTransactionDirection.DEBIT
            )

        else:
            return None

        return CDSLTransactionEvent(
            security_name=security_name,
            isin=isin,
            quantity=quantity,
            direction=direction,
            transaction_datetime=transaction_datetime,
            source="CDSL",
        )