from dataclasses import dataclass
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from pathlib import Path


@dataclass(frozen=True)
class EmailAttachment:
    filename: str
    content_type: str
    content: bytes


@dataclass(frozen=True)
class CDSLEmail:
    subject: str
    sender: str
    recipient: str
    body: str
    attachments: list[EmailAttachment]


class CDSLEmailReader:

    def read(
        self,
        eml_path: str | Path,
    ) -> CDSLEmail:

        eml_path = Path(eml_path)

        if not eml_path.exists():
            raise FileNotFoundError(
                f"Email file not found: {eml_path}"
            )

        with eml_path.open("rb") as email_file:
            message = BytesParser(
                policy=policy.default,
            ).parse(
                email_file,
            )

        return CDSLEmail(
            subject=message.get(
                "Subject",
                "",
            ),
            sender=message.get(
                "From",
                "",
            ),
            recipient=message.get(
                "To",
                "",
            ),
            body=self.extract_body(
                message,
            ),
            attachments=self.extract_attachments(
                message,
            ),
        )
        
    def read_bytes(
        self,
        raw_message:bytes,
    ) -> CDSLEmail:
        message = BytesParser(
            policy=policy.default,
        ).parsebytes(
            raw_message,
        )
        
        return CDSLEmail(
            subject=message.get(
                "Subject",
                ""
            ),
            sender=message.get(
                "From",
                ""
            ),
            recipient=message.get(
                "To",
                ""
            ),
            body=self.extract_body(
                message,
            ),
            attachments=self.extract_attachments(
                message,
            ),
        )

    @staticmethod
    def extract_body(
        message: EmailMessage,
    ) -> str:

        if message.is_multipart():
            html_body = None
            plain_body = None

            for part in message.walk():
                if part.is_multipart():
                    continue

                content_type = part.get_content_type()

                if content_type == "text/html":
                    html_body = part.get_content()

                elif content_type == "text/plain":
                    plain_body = part.get_content()

            if html_body is not None:
                return html_body

            if plain_body is not None:
                return plain_body

            return ""

        if message.get_content_type() in {
            "text/html",
            "text/plain",
        }:
            return message.get_content()

        return ""

    @staticmethod
    def extract_attachments(
        message: EmailMessage,
    ) -> list[EmailAttachment]:

        attachments: list[EmailAttachment] = []

        for part in message.walk():
            if part.is_multipart():
                continue

            filename = part.get_filename()

            if filename is None:
                continue

            content = part.get_payload(
                decode=True,
            )

            if content is None:
                continue

            attachments.append(
                EmailAttachment(
                    filename=filename,
                    content_type=part.get_content_type(),
                    content=content,
                )
            )

        return attachments
