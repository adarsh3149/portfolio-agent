from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter

from app.services.cdsl.cas_pdf_service import (
    CDSLCASEmptyPasswordError,
    CDSLCASEPDFService,
    CDSLCASEncryptionError,
)


PASSWORD = "TEST_CDSL_PASSWORD"


def create_encrypted_pdf(
    path: Path,
    password: str = PASSWORD,
):
    writer = PdfWriter()

    writer.add_blank_page(
        width=612,
        height=792,
    )

    writer.encrypt(password)

    with path.open("wb") as output_file:
        writer.write(output_file)


def create_plain_pdf(path: Path):
    writer = PdfWriter()

    writer.add_blank_page(
        width=612,
        height=792,
    )

    with path.open("wb") as output_file:
        writer.write(output_file)


def test_unlock_encrypted_casl_pdf(
    tmp_path: Path,
):
    encrypted_pdf = tmp_path / "encrypted.pdf"
    decrypted_pdf = tmp_path / "decrypted.pdf"

    create_encrypted_pdf(
        encrypted_pdf,
    )

    service = CDSLCASEPDFService()

    result = service.unlock(
        input_path=encrypted_pdf,
        output_path=decrypted_pdf,
        password=PASSWORD,
    )

    assert result == decrypted_pdf
    assert decrypted_pdf.exists()

    reader = PdfReader(
        str(decrypted_pdf),
    )

    assert reader.is_encrypted is False
    assert len(reader.pages) == 1


def test_unlock_rejects_wrong_password(
    tmp_path: Path,
):
    encrypted_pdf = tmp_path / "encrypted.pdf"
    decrypted_pdf = tmp_path / "decrypted.pdf"

    create_encrypted_pdf(
        encrypted_pdf,
    )

    service = CDSLCASEPDFService()

    with pytest.raises(
        CDSLCASEncryptionError,
    ):
        service.unlock(
            input_path=encrypted_pdf,
            output_path=decrypted_pdf,
            password="WRONG_PASSWORD",
        )

    assert not decrypted_pdf.exists()


def test_unlock_requires_password(
    tmp_path: Path,
):
    encrypted_pdf = tmp_path / "encrypted.pdf"
    decrypted_pdf = tmp_path / "decrypted.pdf"

    create_encrypted_pdf(
        encrypted_pdf,
    )

    service = CDSLCASEPDFService()

    with pytest.raises(
        CDSLCASEmptyPasswordError,
    ):
        service.unlock(
            input_path=encrypted_pdf,
            output_path=decrypted_pdf,
            password="",
        )


def test_unlock_rejects_missing_pdf(
    tmp_path: Path,
):
    service = CDSLCASEPDFService()

    with pytest.raises(
        FileNotFoundError,
    ):
        service.unlock(
            input_path=tmp_path / "missing.pdf",
            output_path=tmp_path / "output.pdf",
            password=PASSWORD,
        )


def test_unlock_handles_already_unencrypted_pdf(
    tmp_path: Path,
):
    input_pdf = tmp_path / "plain.pdf"
    output_pdf = tmp_path / "output.pdf"

    create_plain_pdf(
        input_pdf,
    )

    service = CDSLCASEPDFService()

    result = service.unlock(
        input_path=input_pdf,
        output_path=output_pdf,
        password=PASSWORD,
    )

    assert result == output_pdf
    assert output_pdf.exists()

    reader = PdfReader(
        str(output_pdf),
    )

    assert reader.is_encrypted is False
    assert len(reader.pages) == 1
