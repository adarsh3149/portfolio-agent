# from imapclient import IMAPClient
# import pyzmail
# from bs4 import BeautifulSoup
# from config.settings import EMAIL, APP_PASSWORD, IMAP_SERVER


# def extract_body(message):
#     try:
#         if message.text_part:
#             charset = message.text_part.charset or "utf-8"
#             return message.text_part.get_payload().decode(charset, errors="ignore")

#         elif message.html_part:
#             charset = message.html_part.charset or "utf-8"
#             html = message.html_part.get_payload().decode(charset, errors="ignore")

#             soup = BeautifulSoup(html, "html.parser")
#             return soup.get_text(separator=" ")

#     except Exception as e:
#         print("Decode error:", e)

#     return ""


# def fetch_emails_from_label(label):
#     emails = []

#     with IMAPClient(IMAP_SERVER) as server:
#         server.login(EMAIL, APP_PASSWORD)
#         server.select_folder(label)

#         messages = server.search(['ALL'])

#         for uid in messages:
#             raw_message = server.fetch([uid], ['BODY[]'])
#             message = pyzmail.PyzMessage.factory(raw_message[uid][b'BODY[]'])

#             subject = message.get_subject()
#             body = extract_body(message)

#             emails.append({
#                 "subject": subject,
#                 "body": body
#             })

#     return emails

from imapclient import IMAPClient
import pyzmail
from config.settings import EMAIL, APP_PASSWORD, IMAP_SERVER


from bs4 import BeautifulSoup

def extract_body(message):
    try:
        if message.text_part:
            charset = message.text_part.charset or "utf-8"
            return message.text_part.get_payload().decode(charset, errors="ignore")

        elif message.html_part:
            charset = message.html_part.charset or "utf-8"
            html = message.html_part.get_payload().decode(charset, errors="ignore")

            # 🔥 Convert HTML → clean text
            soup = BeautifulSoup(html, "html.parser")
            return soup.get_text(separator=" ")

    except Exception as e:
        print("⚠️ Decode error:", e)

    return ""


# 🔥 Fetch emails from Gmail
def fetch_emails(label):
    emails = []

    try:
        with IMAPClient(IMAP_SERVER) as server:
            server.login(EMAIL, APP_PASSWORD)

            # 🔥 Read only Zerodha label
            server.select_folder("Zerodha/Allotment")

            messages = server.search(['ALL'])

            for uid in messages:
                raw_message = server.fetch([uid], ['BODY[]'])
                message = pyzmail.PyzMessage.factory(raw_message[uid][b'BODY[]'])

                subject = message.get_subject()
                body = extract_body(message)

                emails.append({
                    "subject": subject,
                    "body": body
                })

    except Exception as e:
        print("❌ Error:", e)

    return emails


# 🧪 Test run
# if __name__ == "__main__":
#     data = fetch_emails()

#     print(f"\n📩 Total Emails Fetched: {len(data)}")

#     for i, email in enumerate(data[:5]):
#         print(f"\n--- Email {i+1} ---")
#         print("Subject:", email["subject"])
#         print("Body Preview:", email["body"][:200])