"""
ECO COMPANY — Email Service
SMTP orqali email yuborish (aiosmtplib)
"""
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from app.config import settings

logger = logging.getLogger("ecocompany")


async def _send_email(to: str, subject: str, html_body: str) -> bool:
    """Email yuborish (low-level)"""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = f"ECO COMPANY <{settings.SMTP_USER}>"
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            use_tls=True,
        )
        logger.info(f"📧 Email yuborildi: {to}")
        return True
    except Exception as e:
        logger.error(f"📧 Email yuborishda xato: {e}")
        return False


async def send_contact_notification(contact) -> bool:
    """Admin ga yangi xabar haqida email"""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #2d6a4f, #40916c); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
            <h2 style="margin: 0;">🌿 Yangi xabar — ECO COMPANY</h2>
        </div>
        <div style="background: #f8f9fa; padding: 20px; border: 1px solid #e9ecef;">
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td style="padding: 8px 0; font-weight: bold; width: 100px;">👤 Ism:</td><td>{contact.name}</td></tr>
                <tr><td style="padding: 8px 0; font-weight: bold;">📧 Email:</td><td>{contact.email or '—'}</td></tr>
                <tr><td style="padding: 8px 0; font-weight: bold;">📞 Telefon:</td><td>{contact.phone or '—'}</td></tr>
                <tr><td style="padding: 8px 0; font-weight: bold;">📝 Mavzu:</td><td>{contact.subject or '—'}</td></tr>
            </table>
            <hr style="border: 1px solid #dee2e6; margin: 15px 0;">
            <p style="font-weight: bold;">💬 Xabar:</p>
            <div style="background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #2d6a4f;">
                {contact.message}
            </div>
        </div>
        <div style="background: #e9ecef; padding: 15px; border-radius: 0 0 10px 10px; text-align: center; color: #6c757d; font-size: 12px;">
            ECO COMPANY — Toza suv, toza hayot
        </div>
    </div>
    """
    return await _send_email(settings.ADMIN_EMAIL, f"🌿 Yangi xabar: {contact.name}", html)


async def send_contact_confirmation(contact) -> bool:
    """Foydalanuvchiga tasdiqlash emaili"""
    if not contact.email:
        return False

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #2d6a4f, #40916c); color: white; padding: 20px; border-radius: 10px 10px 0 0;">
            <h2 style="margin: 0;">🌿 ECO COMPANY</h2>
        </div>
        <div style="background: #f8f9fa; padding: 25px; border: 1px solid #e9ecef;">
            <h3 style="color: #2d6a4f;">Hurmatli {contact.name}!</h3>
            <p>Xabaringiz muvaffaqiyatli qabul qilindi. Tez orada siz bilan bog'lanamiz.</p>
            <p style="color: #6c757d; font-size: 14px;">
                Agar shoshilinch savol bo'lsa, bizga qo'ng'iroq qiling.
            </p>
        </div>
        <div style="background: #e9ecef; padding: 15px; border-radius: 0 0 10px 10px; text-align: center; color: #6c757d; font-size: 12px;">
            ECO COMPANY — Toza suv, toza hayot
        </div>
    </div>
    """
    return await _send_email(contact.email, "✅ Xabaringiz qabul qilindi | ECO COMPANY", html)
