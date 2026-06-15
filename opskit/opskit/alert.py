#!/usr/bin/env python3
import argparse
import requests
import smtplib
from email.mime.text import MIMEText



def _normalize_recipients(to_email):
    if to_email is None:
        return []
    if isinstance(to_email, (list, tuple)):
        return list(to_email)
    return [str(to_email)]


def send_email(
    subject,
    body,
    to_email,
    from_email="alert@localhost",
    smtp_host=None,
    smtp_port=None,
    username=None,
    password=None,
    use_tls=True,
    use_ssl=False,
    timeout=10,
):
    """Send an email alert.

    Parameters:
    - subject, body: message
    - to_email: str or list of recipient addresses
    - from_email: sender address
    - smtp_host/smtp_port: if omitted, will try localhost without auth
    - username/password: optional auth for remote SMTP
    - use_tls/use_ssl: connection options
    Returns True on success, False on failure.
    """
    recipients = _normalize_recipients(to_email)
    if not recipients:
        print("No recipients provided to send_email")
        return False

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = ", ".join(recipients)

    
    if not smtp_host:
        try:
            with smtplib.SMTP("localhost", timeout=timeout) as server:
                server.send_message(msg)
            print("Alert email sent via localhost to %s" % recipients)
            return True
        except Exception as e:
            print("Local SMTP send failed:", e)
            
    
    host = smtp_host or "smtp.gmail.com"
    port = smtp_port or (465 if use_ssl else 587)

    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=timeout)
        else:
            server = smtplib.SMTP(host, port, timeout=timeout)

        with server:
            server.ehlo()
            if use_tls and not use_ssl:
                server.starttls()
                server.ehlo()
            if username and password:
                server.login(username, password)
            server.send_message(msg)

        print("Alert email sent via %s to %s" % (host, recipients))
        return True
    except Exception as e:
        print("Failed to send alert email:", e)
        return False


def send_webhook(url, payload, headers=None, timeout=5):
    """Send a JSON payload to an HTTP webhook (e.g., Slack, Teams).

    Returns True on 2xx response, False otherwise.
    """
    try:
        resp = requests.post(url, json=payload, headers=headers or {}, timeout=timeout)
        if 200 <= resp.status_code < 300:
            print("Webhook delivered to %s (status=%s)" % (url, resp.status_code))
            return True
        print("Webhook failed (%s): %s" % (resp.status_code, resp.text))
        return False
    except Exception as e:
        print("Error sending webhook to %s:" % url, e)
        return False


def send_alert(
    subject,
    body,
    to_email=None,
    webhook_url=None,
    smtp_kwargs=None,
):
    """Convenience helper to send email and/or webhook alerts.

    Returns a dict with results for `email` and `webhook` keys.
    """
    results = {"email": None, "webhook": None}
    smtp_kwargs = smtp_kwargs or {}

    if to_email:
        results["email"] = send_email(subject, body, to_email, **smtp_kwargs)

    if webhook_url:
        payload = {"text": f"{subject}\n\n{body}"}
        results["webhook"] = send_webhook(webhook_url, payload)

    return results


def main():
    parser = argparse.ArgumentParser(description="Send alert emails and/or webhook notifications.")
    parser.add_argument("--subject", required=True, help="Alert subject")
    parser.add_argument("--body", required=True, help="Alert message body")
    parser.add_argument("--to-email", help="Recipient email address or comma-separated list")
    parser.add_argument("--from-email", default="alert@localhost", help="Sender email address")
    parser.add_argument("--smtp-host", help="SMTP server host")
    parser.add_argument("--smtp-port", type=int, help="SMTP server port")
    parser.add_argument("--username", help="SMTP username")
    parser.add_argument("--password", help="SMTP password")
    parser.add_argument("--webhook", help="Webhook URL to notify")

    args = parser.parse_args()

    to_email = None
    if args.to_email:
        to_email = [email.strip() for email in args.to_email.split(",") if email.strip()]

    smtp_kwargs = {
        "from_email": args.from_email,
        "smtp_host": args.smtp_host,
        "smtp_port": args.smtp_port,
        "username": args.username,
        "password": args.password,
    }

    result = send_alert(
        subject=args.subject,
        body=args.body,
        to_email=to_email,
        webhook_url=args.webhook,
        smtp_kwargs=smtp_kwargs,
    )

    print("Alert results:")
    print(result)


__all__ = [
    "send_email",
    "send_webhook",
    "send_alert",
    "main",
]

if __name__ == "__main__":
    main()
