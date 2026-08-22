from decimal import Decimal
from pathlib import Path

from app.schemas.cdsl import (
    CDSLTransactionDirection,
)
from app.services.cdsl.daily_email_parser import (
    CDSLDailyEmailParser,
)
from app.services.cdsl.email_reader import (
    CDSLEmailReader,
)


REAL_CDSL_EMAIL = (
    Path(__file__).parent
    / "fixtures"
    / "cdsl"
    / "daily_transaction.eml"
)


def create_cdsl_html(
    rows: str,
) -> str:

    return f"""
    <html>
        <body>
            <table>
                <tr>
                    <th>Sr. No.</th>
                    <th>Company Name</th>
                    <th>ISIN</th>
                    <th>Quantity</th>
                    <th>Debit / Credit</th>
                    <th>Date and Time</th>
                </tr>

                {rows}

            </table>
        </body>
    </html>
    """


def test_parse_single_cdsl_transaction():

    parser = CDSLDailyEmailParser()

    html = create_cdsl_html(
        """
        <tr>
            <td>1</td>
            <td>Edelweiss Mid Cap Fund</td>
            <td>INF843K01AO4</td>
            <td>0.771</td>
            <td>Credit</td>
            <td>10/08/2026 23:17:03</td>
        </tr>
        """
    )

    result = parser.parse(
        html,
    )

    assert len(result) == 1

    event = result[0]

    assert event.security_name == (
        "Edelweiss Mid Cap Fund"
    )

    assert event.isin == "INF843K01AO4"

    assert event.quantity == Decimal(
        "0.771"
    )

    assert event.direction == (
        CDSLTransactionDirection.CREDIT
    )

    assert event.transaction_datetime.strftime(
        "%d/%m/%Y %H:%M:%S"
    ) == "10/08/2026 23:17:03"


def test_parse_multiple_cdsl_transactions():

    parser = CDSLDailyEmailParser()

    html = create_cdsl_html(
        """
        <tr>
            <td>1</td>
            <td>Edelweiss Mid Cap Fund</td>
            <td>INF843K01AO4</td>
            <td>0.771</td>
            <td>Credit</td>
            <td>10/08/2026 23:17:03</td>
        </tr>

        <tr>
            <td>2</td>
            <td>Invesco Mid Cap Fund</td>
            <td>INF205K013T3</td>
            <td>1.847</td>
            <td>Credit</td>
            <td>10/08/2026 23:18:03</td>
        </tr>
        """
    )

    result = parser.parse(
        html,
    )

    assert len(result) == 2

    assert result[0].isin == (
        "INF843K01AO4"
    )

    assert result[1].isin == (
        "INF205K013T3"
    )

    assert result[0].quantity == Decimal(
        "0.771"
    )

    assert result[1].quantity == Decimal(
        "1.847"
    )


def test_parse_debit_transaction():

    parser = CDSLDailyEmailParser()

    html = create_cdsl_html(
        """
        <tr>
            <td>1</td>
            <td>Edelweiss Mid Cap Fund</td>
            <td>INF843K01AO4</td>
            <td>0.771</td>
            <td>Debit</td>
            <td>10/08/2026 23:17:03</td>
        </tr>
        """
    )

    result = parser.parse(
        html,
    )

    assert len(result) == 1

    assert result[0].direction == (
        CDSLTransactionDirection.DEBIT
    )


def test_parse_empty_email():

    parser = CDSLDailyEmailParser()

    result = parser.parse(
        "",
    )

    assert result == []


def test_parse_ignores_irrelevant_content():

    parser = CDSLDailyEmailParser()

    html = """
    <html>
        <body>
            <h1>Some unrelated email</h1>
            <p>No transaction information.</p>

            <table>
                <tr>
                    <th>Name</th>
                    <th>Value</th>
                </tr>

                <tr>
                    <td>Something</td>
                    <td>123</td>
                </tr>
            </table>
        </body>
    </html>
    """

    result = parser.parse(
        html,
    )

    assert result == []


def test_parse_realistic_cdsl_daily_email():

    reader = CDSLEmailReader()

    email = reader.read(
        REAL_CDSL_EMAIL,
    )

    parser = CDSLDailyEmailParser()

    result = parser.parse(
        email.body,
    )

    assert len(result) == 2

    first = result[0]

    assert first.isin == (
        "INF205K013T3"
    )

    assert first.quantity == Decimal(
        "1.841"
    )

    assert first.direction == (
        CDSLTransactionDirection.CREDIT
    )

    second = result[1]

    assert second.isin == (
        "INF843K01AO4"
    )

    assert second.quantity == Decimal(
        "0.765"
    )

    assert second.direction == (
        CDSLTransactionDirection.CREDIT
    )