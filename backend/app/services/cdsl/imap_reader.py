from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from pathlib import Path
import imaplib
import os
from app.services.cdsl.email_reader import (
    CDSLEmail,
    CDSLEmailReader,
)

@dataclass(frozen=True)
class IMAPEmail:
    uid: str
    raw_message: bytes


class CDSLIMAPReader:
    """
    Reads emails from Gmail using IMAP.

    This class is responsible only for Gmail/IMAP access.
    Email parsing remains the responsibility of CDSLEmailReader.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:

        self.host = (
            host
            or os.getenv("GMAIL_IMAP_HOST")
            or "imap.gmail.com"
        )

        self.port = (
            port
            or int(
                os.getenv(
                    "GMAIL_IMAP_PORT",
                    "993",
                )
            )
        )

        self.username = (
            username
            or os.getenv("GMAIL_USERNAME")
        )

        self.password = (
            password
            or os.getenv("GMAIL_APP_PASSWORD")
        )

        if not self.username:
            raise ValueError(
                "GMAIL_USERNAME is not configured"
            )

        if not self.password:
            raise ValueError(
                "GMAIL_APP_PASSWORD is not configured"
            )

    def connect(self) -> imaplib.IMAP4_SSL:
        """
        Establish an authenticated Gmail IMAP connection.
        """

        mail = imaplib.IMAP4_SSL(
            self.host,
            self.port,
        )

        mail.login(
            self.username,
            self.password,
        )

        return mail

    def list_mailboxes(
        self,
    ) -> list[str]:

        mail = self.connect()

        try:
            status, mailboxes = mail.list()

            if status != "OK":
                raise RuntimeError(
                    "Unable to list Gmail mailboxes"
                )

            result: list[str] = []

            for mailbox in mailboxes or []:
                if isinstance(mailbox, bytes):
                    result.append(
                        mailbox.decode(
                            "utf-8",
                            errors="replace",
                        )
                    )

            return result

        finally:
            try:
                mail.logout()
            except imaplib.IMAP4.error:
                pass

    def search(
        self,
        mailbox: str = "INBOX",
        criteria: str = "ALL",
    ) -> list[str]:

        mail = self.connect()

        try:
            status, _ = mail.select(
                mailbox,
                readonly=True,
            )

            if status != "OK":
                raise RuntimeError(
                    f"Unable to select mailbox: {mailbox}"
                )

            status, data = mail.uid(
                "SEARCH",
                None,
                criteria,
            )

            if status != "OK":
                raise RuntimeError(
                    "Gmail IMAP search failed"
                )

            if not data or not data[0]:
                return []

            return data[0].decode().split()

        finally:
            try:
                mail.logout()
            except imaplib.IMAP4.error:
                pass

    def fetch(
        self,
        uid: str,
        mailbox: str = "INBOX",
    ) -> IMAPEmail:

        mail = self.connect()

        try:
            status, _ = mail.select(
                mailbox,
                readonly=True,
            )

            if status != "OK":
                raise RuntimeError(
                    f"Unable to select mailbox: {mailbox}"
                )

            status, data = mail.uid(
                "FETCH",
                uid,
                "(RFC822)",
            )

            if status != "OK":
                raise RuntimeError(
                    f"Unable to fetch email UID: {uid}"
                )

            raw_message = self._extract_raw_message(
                data,
            )

            return IMAPEmail(
                uid=uid,
                raw_message=raw_message,
            )

        finally:
            try:
                mail.logout()
            except imaplib.IMAP4.error:
                pass
            
    def fetch_email(
        self,
        uid:str,
        mailbox: str = "INBOX",
    ) -> CDSLEmail:
        
        imap_email = self.fetch(
            uid=uid,
            mailbox=mailbox
        )
        
        return CDSLEmailReader().read_bytes(
            imap_email.raw_message,
        )

    @staticmethod
    def _extract_raw_message(
        data,
    ) -> bytes:

        for item in data or []:
            if not isinstance(item, tuple):
                continue

            if len(item) < 2:
                continue

            raw_message = item[1]

            if isinstance(
                raw_message,
                bytes,
            ):
                return raw_message

        raise RuntimeError(
            "No raw email message returned by Gmail"
        )
