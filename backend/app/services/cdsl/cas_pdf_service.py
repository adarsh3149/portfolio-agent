from pathlib import Path

from pypdf import PdfReader, PdfWriter


class CDSLCASEmptyPasswordError(ValueError):
    """Raised when no CAS PDF password is supplied."""


class CDSLCASEncryptionError(ValueError):
    """Raised when a CAS PDF cannot be unlocked."""


class CDSLCASEPDFService:
    """
    Unlocks password-protected CDSL CAS PDFs.

    The password is accepted only at runtime and is never
    persisted or included in exception messages.
    """

    def unlock(
        self,
        input_path: str | Path,
        output_path: str | Path,
        password: str,
    ) -> Path:

        if not password:
            raise CDSLCASEmptyPasswordError(
                "CAS PDF password is required."
            )

        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(
                f"CAS PDF not found: {input_path}"
            )

        reader = PdfReader(str(input_path))

        if not reader.is_encrypted:
            self._write_pdf(
                reader,
                output_path,
            )
            return output_path

        try:
            result = reader.decrypt(password)
        except Exception as exc:
            raise CDSLCASEncryptionError(
                "Unable to unlock CAS PDF."
            ) from exc

        if result == 0:
            raise CDSLCASEncryptionError(
                "Unable to unlock CAS PDF."
            )

        self._write_pdf(
            reader,
            output_path,
        )

        return output_path

    @staticmethod
    def _write_pdf(
        reader: PdfReader,
        output_path: Path,
    ) -> None:

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        with output_path.open("wb") as output_file:
            writer.write(output_file)