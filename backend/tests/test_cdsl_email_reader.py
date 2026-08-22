from email.message import EmailMessage
from pathlib import Path
from decimal import Decimal

from app.schemas.cdsl import (
    CDSLTransactionDirection,
)

from app.services.cdsl.email_reader import CDSLEmailReader
from app.services.cdsl.daily_email_parser import (
    CDSLDailyEmailParser,
)


REAL_CDSL_EMAIL = (
    Path(__file__).parent
    / "fixtures"
    / "cdsl"
    / "daily_transaction.eml"
)


def test_parse_real_cdsl_email_fixture():

    reader = CDSLEmailReader()

    email = reader.read(
        REAL_CDSL_EMAIL,
    )

    parser = CDSLDailyEmailParser()

    result = parser.parse(
        email.body,
    )

    assert len(result) == 2

    assert result[0].security_name.startswith(
        "INVESCO ASSET MANAGEMENT"
    )

    assert result[0].isin == "INF205K013T3"
    assert result[0].quantity == Decimal("1.841")
    assert result[0].direction == (
        CDSLTransactionDirection.CREDIT
    )

    assert result[1].security_name.startswith(
        "EDELWEISS AM LTD"
    )

    assert result[1].isin == "INF843K01AO4"
    assert result[1].quantity == Decimal("0.765")
    assert result[1].direction == (
        CDSLTransactionDirection.CREDIT
    )


def test_read_plain_text_email(
    tmp_path: Path,
):

    email_path = tmp_path / "plain.eml"

    message = EmailMessage()

    message["Subject"] = "CDSL Transaction"
    message["From"] = "cdsl@example.com"
    message["To"] = "user@example.com"

    message.set_content(
        "This is a plain text CDSL email."
    )

    email_path.write_bytes(
        message.as_bytes()
    )

    reader = CDSLEmailReader()

    result = reader.read(
        email_path,
    )

    assert result.body == (
        "This is a plain text CDSL email.\n"
    )


def test_read_html_email(
    tmp_path: Path,
):

    email_path = tmp_path / "html.eml"

    message = EmailMessage()

    message["Subject"] = "CDSL Transaction"
    message["From"] = "cdsl@example.com"
    message["To"] = "user@example.com"

    message.set_content(
        "Fallback plain text."
    )

    message.add_alternative(
        """
        <html>
            <body>
                <h1>CDSL Transaction</h1>
                <p>Transaction completed.</p>
            </body>
        </html>
        """,
        subtype="html",
    )

    email_path.write_bytes(
        message.as_bytes()
    )

    reader = CDSLEmailReader()

    result = reader.read(
        email_path,
    )

    assert "CDSL Transaction" in result.body
    assert "Transaction completed." in result.body


def test_extracts_pdf_attachment(
    tmp_path: Path,
):

    email_path = tmp_path / "attachment.eml"

    message = EmailMessage()

    message["Subject"] = "CDSL CAS"
    message["From"] = "cdsl@example.com"
    message["To"] = "user@example.com"

    message.set_content(
        "Please find the CAS attached."
    )

    message.add_attachment(
        b"%PDF-test-content",
        maintype="application",
        subtype="pdf",
        filename="cas.pdf",
    )

    email_path.write_bytes(
        message.as_bytes()
    )

    reader = CDSLEmailReader()

    result = reader.read(
        email_path,
    )

    assert len(result.attachments) == 1

    attachment = result.attachments[0]

    assert attachment.filename == "cas.pdf"
    assert attachment.content == (
        b"%PDF-test-content"
    )


def test_extracts_multiple_attachments(
    tmp_path: Path,
):

    email_path = tmp_path / "multiple.eml"

    message = EmailMessage()

    message["Subject"] = "CDSL Documents"
    message["From"] = "cdsl@example.com"
    message["To"] = "user@example.com"

    message.set_content(
        "Multiple documents attached."
    )

    message.add_attachment(
        b"PDF-ONE",
        maintype="application",
        subtype="pdf",
        filename="cas1.pdf",
    )

    message.add_attachment(
        b"PDF-TWO",
        maintype="application",
        subtype="pdf",
        filename="cas2.pdf",
    )

    email_path.write_bytes(
        message.as_bytes()
    )

    reader = CDSLEmailReader()

    result = reader.read(
        email_path,
    )

    assert len(result.attachments) == 2

    filenames = {
        attachment.filename
        for attachment in result.attachments
    }

    assert filenames == {
        "cas1.pdf",
        "cas2.pdf",
    }


def test_no_attachment_returns_empty_list(
    tmp_path: Path,
):

    email_path = tmp_path / "no_attachment.eml"

    message = EmailMessage()

    message["Subject"] = "CDSL Notification"
    message["From"] = "cdsl@example.com"
    message["To"] = "user@example.com"

    message.set_content(
        "No attachment in this email."
    )

    email_path.write_bytes(
        message.as_bytes()
    )

    reader = CDSLEmailReader()

    result = reader.read(
        email_path,
    )

    assert result.attachments == []


def test_missing_eml_is_rejected(
    tmp_path: Path,
):

    reader = CDSLEmailReader()

    missing_file = (
        tmp_path / "missing.eml"
    )

    try:
        reader.read(
            missing_file,
        )
        assert False, (
            "Expected FileNotFoundError"
        )
    except FileNotFoundError:
        pass