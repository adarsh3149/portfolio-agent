# # import smtplib
# # from email.mime.text import MIMEText
# # from config.settings import EMAIL, APP_PASSWORD


# # def send_email(subject, body):
# #     msg = MIMEText(body)
# #     msg["Subject"] = subject
# #     msg["From"] = EMAIL
# #     msg["To"] = EMAIL

# #     try:
# #         with smtplib.SMTP("smtp.gmail.com", 587) as server:
# #             server.starttls()
# #             server.login(EMAIL, APP_PASSWORD)
# #             server.send_message(msg)

# #         print("✅ Email sent successfully!")

# #     except Exception as e:
# #         print("❌ Failed to send email:", e)

# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from config.settings import EMAIL, APP_PASSWORD


# def send_email(subject, report_text):
#     msg = MIMEMultipart("alternative")
#     msg["Subject"] = subject
#     msg["From"] = EMAIL
#     msg["To"] = EMAIL

#     # 🔥 Convert report to HTML
#     html = f"""
#     <html>
#         <body style="font-family: Arial; background:#f5f5f5; padding:20px;">
#             <div style="max-width:600px; margin:auto; background:white; padding:20px; border-radius:10px;">
#                 <h2 style="text-align:center;">📊 Portfolio Report</h2>
#                 <pre style="font-size:14px; line-height:1.6;">{report_text}</pre>
#             </div>
#         </body>
#     </html>
#     """

#     msg.attach(MIMEText(html, "html"))

#     try:
#         with smtplib.SMTP("smtp.gmail.com", 587) as server:
#             server.starttls()
#             server.login(EMAIL, APP_PASSWORD)
#             server.send_message(msg)

#         print("✅ Email sent successfully!")

#     except Exception as e:
#         print("❌ Failed to send email:", e)

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config.settings import EMAIL, APP_PASSWORD


def send_email(subject, report_data):
    report_text = report_data["report"]
    ai_text = report_data["ai"]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = EMAIL

    # 🔥 Convert line breaks
    report_html = report_text.replace("\n", "<br>")
    ai_html = ai_text.replace("\n", "<br>")

    html = f"""
    <html>
    <body style="font-family: Arial; background:#f4f6f8; padding:20px;">
        
        <div style="max-width:700px; margin:auto;">

            <!-- HEADER -->
            <div style="background:#1f2937; color:white; padding:15px; border-radius:10px 10px 0 0;">
                <h2 style="margin:0;">📊 Daily Portfolio Report</h2>
            </div>

            <!-- MAIN CARD -->
            <div style="background:white; padding:20px; border-radius:0 0 10px 10px;">

                <!-- SUMMARY -->
                <h3 style="color:#111827;">Portfolio Summary</h3>
                <div style="font-size:14px; line-height:1.6;">
                    {report_html}
                </div>

                <hr style="margin:20px 0;">

                <!-- AI INSIGHTS -->
                <h3 style="color:#111827;">🤖 AI Insights</h3>
                <div style="background:#f9fafb; padding:15px; border-radius:8px; font-size:14px;">
                    {ai_html}
                </div>

            </div>

            <!-- FOOTER -->
            <div style="text-align:center; font-size:12px; color:#6b7280; margin-top:10px;">
                Generated automatically by your Portfolio Agent 🚀
            </div>

        </div>

    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL, APP_PASSWORD)
            server.send_message(msg)

        print("✅ Email sent!")

    except Exception as e:
        print("❌ Email failed:", e)