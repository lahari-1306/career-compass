"""
Production Server-Side Email Service for CareerCompass.
Handles SMTP delivery using credentials from environment variables:
- MAIL_SERVER (e.g. smtp.gmail.com, smtp.sendgrid.net, etc.)
- MAIL_PORT (e.g. 587 or 465)
- MAIL_USERNAME
- MAIL_PASSWORD
- MAIL_FROM (e.g. "CareerCompass <no-reply@careercompass.org>")
- MAIL_USE_TLS (default: True)

When credentials are not configured in local/dev environments,
it safely logs the rendered email to data/email_logs.json so the system
never crashes while remaining 100% production ready when env vars are set.
"""

import os
import smtplib
import ssl
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger("careercompass.email")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
LOG_FILE = os.path.join(DATA_DIR, "email_logs.json")
IST = timezone(timedelta(hours=5, minutes=30))


class EmailService:
    @staticmethod
    def _is_configured() -> bool:
        server = os.environ.get("MAIL_SERVER", "").strip()
        user = os.environ.get("MAIL_USERNAME", "").strip()
        pwd = os.environ.get("MAIL_PASSWORD", "").strip()
        return bool(server and user and pwd)

    @staticmethod
    def _log_email(to_email: str, subject: str, body_text: str, body_html: str, template_type: str, status: str) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        logs = []
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []
        
        entry = {
            "timestamp": datetime.now(IST).isoformat(),
            "to": to_email,
            "subject": subject,
            "template_type": template_type,
            "status": status,
            "preview": body_text[:200]
        }
        logs.insert(0, entry)
        # Keep last 100 logged emails
        logs = logs[:100]
        try:
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to write email log: {e}")

    @staticmethod
    def send_email(to_email: str, subject: str, body_text: str, body_html: Optional[str] = None, template_type: str = "general") -> Dict[str, Any]:
        """
        Sends an email using standard SMTP.
        If SMTP is configured, dispatches real email.
        Otherwise, records in audit log for dev/test environments.
        """
        mail_from = os.environ.get("MAIL_FROM", "CareerCompass <noreply@careercompass.gov.in>")
        
        if not EmailService._is_configured():
            logger.info(f"[DEV/TEST EMAIL] To: {to_email} | Subject: {subject}")
            EmailService._log_email(to_email, subject, body_text, body_html or body_text, template_type, "QUEUED_DEV_LOGGED")
            return {
                "status": "queued_dev_logged",
                "message": "SMTP not configured. Email logged to data/email_logs.json",
                "to": to_email,
                "subject": subject
            }

        server_host = os.environ.get("MAIL_SERVER")
        server_port = int(os.environ.get("MAIL_PORT", 587))
        username = os.environ.get("MAIL_USERNAME")
        password = os.environ.get("MAIL_PASSWORD")
        use_tls = os.environ.get("MAIL_USE_TLS", "true").lower() in ("1", "true", "yes")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = mail_from
        msg["To"] = to_email

        part1 = MIMEText(body_text, "plain", "utf-8")
        msg.attach(part1)

        if body_html:
            part2 = MIMEText(body_html, "html", "utf-8")
            msg.attach(part2)

        try:
            if server_port == 465:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(server_host, server_port, context=context) as server:
                    server.login(username, password)
                    server.sendmail(mail_from, [to_email], msg.as_string())
            else:
                with smtplib.SMTP(server_host, server_port, timeout=15) as server:
                    if use_tls:
                        context = ssl.create_default_context()
                        server.starttls(context=context)
                    server.login(username, password)
                    server.sendmail(mail_from, [to_email], msg.as_string())

            EmailService._log_email(to_email, subject, body_text, body_html or body_text, template_type, "SENT")
            return {"status": "sent", "to": to_email}
        except Exception as e:
            logger.error(f"SMTP sending failed: {e}")
            EmailService._log_email(to_email, subject, body_text, body_html or body_text, template_type, f"FAILED: {str(e)}")
            return {"status": "failed", "error": str(e)}

    # ====================================================
    # EMAIL TEMPLATES
    # ====================================================

    @staticmethod
    def send_welcome_email(user_name: str, to_email: str) -> Dict[str, Any]:
        subject = "Welcome to CareerCompass — Your Personal Career & Education Navigator"
        text = f"""Hello {user_name},

Welcome to CareerCompass! Your account has been successfully created.

With CareerCompass, you can:
• Receive verified notification updates for exams, counselling, jobs, and scholarships.
• Set up My Career Radar to get personalized alerts tailored to your exact qualification and stream.
• Explore qualification-aware career pathways and exam preparation resources.
• Receive direct deadline reminders so you never miss an official registration window.

Access your dashboard: https://career-compass.onrender.com

Wishing you success in your education and career journey,
The CareerCompass Team
"""
        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 8px; background: #ffffff;">
          <div style="border-bottom: 2px solid #2563eb; padding-bottom: 16px; margin-bottom: 24px;">
            <h1 style="color: #1e293b; font-size: 22px; margin: 0;">🧭 CareerCompass</h1>
            <p style="color: #64748b; font-size: 14px; margin: 4px 0 0 0;">Official Indian Education & Career Navigation Portal</p>
          </div>
          <h2 style="color: #0f172a; font-size: 18px;">Welcome, {user_name}!</h2>
          <p style="color: #334155; font-size: 15px; line-height: 1.6;">
            Your personal CareerCompass account is active. We are dedicated to ensuring you never miss a verified career or educational opportunity.
          </p>
          <div style="background: #f8fafc; border-left: 4px solid #2563eb; padding: 14px 16px; margin: 20px 0; border-radius: 4px;">
            <p style="margin: 0; font-weight: 600; color: #1e293b;">Next Steps to Activate Your Radar:</p>
            <ul style="margin: 8px 0 0 0; padding-left: 20px; color: #475569; font-size: 14px; line-height: 1.6;">
              <li>Set your exact educational qualification in your Profile.</li>
              <li>Enable browser push and email alerts for deadline reminders.</li>
              <li>Explore verified study plans and topic-wise syllabi in the Exam Preparation Hub.</li>
            </ul>
          </div>
          <div style="text-align: center; margin: 30px 0;">
            <a href="https://career-compass.onrender.com" style="background: #2563eb; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; display: inline-block;">Open CareerCompass Dashboard</a>
          </div>
          <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;" />
          <p style="color: #94a3b8; font-size: 12px; margin: 0; text-align: center;">
            CareerCompass • Empowering Indian Students with Verified Educational Intelligence
          </p>
        </div>
        """
        return EmailService.send_email(to_email, subject, text, html, "welcome")

    @staticmethod
    def send_password_reset_email(to_email: str, reset_token: str, app_url: str = "https://career-compass.onrender.com") -> Dict[str, Any]:
        reset_link = f"{app_url}/?reset_token={reset_token}#reset-password"
        subject = "Reset Your CareerCompass Account Password"
        text = f"""Hello,

You requested a password reset for your CareerCompass account.

Click the link below or copy and paste it into your browser to set a new password:
{reset_link}

This link is valid for 2 hours. If you did not request this reset, you can safely ignore this email.

The CareerCompass Team
"""
        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 8px; background: #ffffff;">
          <div style="border-bottom: 2px solid #2563eb; padding-bottom: 16px; margin-bottom: 24px;">
            <h1 style="color: #1e293b; font-size: 22px; margin: 0;">🧭 CareerCompass</h1>
          </div>
          <h2 style="color: #0f172a; font-size: 18px;">Password Reset Request</h2>
          <p style="color: #334155; font-size: 15px; line-height: 1.6;">
            We received a request to reset your password. Click the button below to choose a new password for your account:
          </p>
          <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_link}" style="background: #2563eb; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; display: inline-block;">Reset Password</a>
          </div>
          <p style="color: #64748b; font-size: 13px;">
            If the button doesn't work, copy this link into your browser:<br/>
            <a href="{reset_link}" style="color: #2563eb;">{reset_link}</a>
          </p>
          <p style="color: #94a3b8; font-size: 13px;">This link will expire in 2 hours. If you did not initiate this request, no action is required.</p>
        </div>
        """
        return EmailService.send_email(to_email, subject, text, html, "password_reset")

    @staticmethod
    def send_opportunity_alert(to_email: str, user_name: str, opp_title: str, org: str, deadline: str, deep_link: str, reason: str) -> Dict[str, Any]:
        subject = f"🎯 Career Alert: {opp_title} ({org})"
        text = f"""Hello {user_name},

A new verified opportunity matching your profile has been detected on My Career Radar:

• Opportunity: {opp_title}
• Organization: {org}
• Application Deadline: {deadline}
• Why you are seeing this: {reason}

View full official notification: {deep_link}

Never miss a verified deadline. Manage your notification preferences anytime on CareerCompass.

The CareerCompass Team
"""
        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 8px; background: #ffffff;">
          <div style="border-bottom: 2px solid #2563eb; padding-bottom: 16px; margin-bottom: 20px;">
            <h1 style="color: #1e293b; font-size: 20px; margin: 0;">🧭 CareerCompass — Radar Alert</h1>
          </div>
          <h2 style="color: #1e293b; font-size: 18px; margin-top: 0;">{opp_title}</h2>
          <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 16px; margin: 16px 0;">
            <p style="margin: 0 0 8px 0; color: #1e3a8a; font-weight: 600;">Organization: {org}</p>
            <p style="margin: 0 0 8px 0; color: #1e3a8a;"><strong>Application Deadline:</strong> {deadline}</p>
            <p style="margin: 0; color: #2563eb; font-size: 13px;">💡 <em>Why this matches: {reason}</em></p>
          </div>
          <div style="text-align: center; margin: 24px 0;">
            <a href="{deep_link}" style="background: #2563eb; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; display: inline-block;">View Official Notification</a>
          </div>
          <p style="color: #64748b; font-size: 13px;">You received this email because your notification preferences allow Radar alerts for matching educational opportunities.</p>
        </div>
        """
        return EmailService.send_email(to_email, subject, text, html, "opportunity_alert")

    @staticmethod
    def send_deadline_reminder(to_email: str, user_name: str, opp_title: str, org: str, days_left: int, official_url: str) -> Dict[str, Any]:
        subject = f"⚠️ URGENT: Deadline Approaching for {opp_title} ({days_left} Days Left)"
        text = f"""Hello {user_name},

URGENT REMINDER: The application deadline for {opp_title} by {org} closes in {days_left} days!

Official Portal: {official_url}

Please ensure you submit your application before the official closing time.

The CareerCompass Team
"""
        html = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; border: 1px solid #fed7aa; border-radius: 8px; background: #fffbeb;">
          <div style="border-bottom: 2px solid #f97316; padding-bottom: 12px; margin-bottom: 16px;">
            <h2 style="color: #9a3412; font-size: 18px; margin: 0;">⚠️ Urgent Deadline Reminder</h2>
          </div>
          <h3 style="color: #7c2d12; margin-top: 0;">{opp_title}</h3>
          <p style="color: #9a3412; font-size: 16px; font-weight: bold;">
            Only {days_left} days remaining before applications close!
          </p>
          <p style="color: #431407; font-size: 14px;"><strong>Conducting Authority:</strong> {org}</p>
          <div style="text-align: center; margin: 24px 0;">
            <a href="{official_url}" style="background: #ea580c; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 6px; font-weight: 600; display: inline-block;">Complete Application Now</a>
          </div>
        </div>
        """
        return EmailService.send_email(to_email, subject, text, html, "deadline_reminder")
