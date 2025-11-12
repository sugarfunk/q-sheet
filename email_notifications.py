"""
Email notification system using SMTP
Simple, standalone email functionality
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, date, timedelta
from database import get_setting
import models


def send_email(to_email, subject, body_html, body_text=None):
    """
    Send an email using configured SMTP settings
    Returns True if successful, False otherwise
    """
    # Check if SMTP is enabled
    smtp_enabled = get_setting('smtp_enabled', '0') == '1'
    if not smtp_enabled:
        print("SMTP is not enabled in settings")
        return False

    # Get SMTP configuration
    smtp_host = get_setting('smtp_host')
    smtp_port = int(get_setting('smtp_port', '587'))
    smtp_username = get_setting('smtp_username')
    smtp_password = get_setting('smtp_password')
    from_email = get_setting('smtp_from_email')
    from_name = get_setting('smtp_from_name', 'F3 Q-Sheet')

    if not all([smtp_host, smtp_username, smtp_password, from_email]):
        print("SMTP configuration incomplete")
        return False

    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email

        # Add plain text and HTML parts
        if body_text:
            part1 = MIMEText(body_text, 'plain')
            msg.attach(part1)

        part2 = MIMEText(body_html, 'html')
        msg.attach(part2)

        # Send email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        print(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def send_q_reminder(signup):
    """Send reminder email to Q before their workout"""
    if not signup['q_email']:
        return False

    subject = f"Reminder: You're Q'ing at {signup['location_name']} on {signup['date']}"

    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #dc2626; color: white; padding: 20px; text-align: center;">
            <h1>Q Reminder</h1>
        </div>

        <div style="padding: 20px;">
            <p>Hey <strong>{signup['q_name']}</strong>!</p>

            <p>This is your friendly reminder that you're scheduled to Q in 2 days:</p>

            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Location:</strong> {signup['location_name']}</p>
                <p style="margin: 5px 0;"><strong>Address:</strong> {signup['address']}</p>
                <p style="margin: 5px 0;"><strong>Date:</strong> {signup['date']}</p>
                <p style="margin: 5px 0;"><strong>Time:</strong> {signup['time']}</p>
                <p style="margin: 5px 0;"><strong>Type:</strong> {signup['workout_type']}</p>
            </div>

            <p><strong>Q Tips:</strong></p>
            <ul>
                <li>Arrive 10 minutes early to set up</li>
                <li>Bring your energy and enthusiasm!</li>
                <li>Have a backup plan in case of weather</li>
                <li>Remember the 5 core principles of F3</li>
            </ul>

            <p>Thanks for leading the PAX!</p>
        </div>

        <div style="background-color: #1f2937; color: white; padding: 15px; text-align: center; font-size: 12px;">
            <p>F3 Q-Sheet - Keeping workouts covered</p>
        </div>
    </body>
    </html>
    """

    body_text = f"""
Q Reminder

Hey {signup['q_name']}!

This is your friendly reminder that you're scheduled to Q in 2 days:

Location: {signup['location_name']}
Address: {signup['address']}
Date: {signup['date']}
Time: {signup['time']}
Type: {signup['workout_type']}

Q Tips:
- Arrive 10 minutes early to set up
- Bring your energy and enthusiasm!
- Have a backup plan in case of weather
- Remember the 5 core principles of F3

Thanks for leading the PAX!

---
F3 Q-Sheet - Keeping workouts covered
    """

    return send_email(signup['q_email'], subject, body_html, body_text)


def send_reminders_batch():
    """
    Send reminder emails for all upcoming Qs that need reminders
    This should be run as a daily cron job
    """
    days_before = int(get_setting('reminder_days_before', '2'))
    reminder_date = (date.today() + timedelta(days=days_before)).strftime('%Y-%m-%d')

    # Get signups that need reminders
    with models.db_transaction() as conn:
        signups = conn.execute(
            '''SELECT s.*, w.day_of_week, w.time, w.workout_type,
                      l.name as location_name, l.address
               FROM q_signups s
               JOIN workouts w ON s.workout_id = w.id
               JOIN locations l ON w.location_id = l.id
               WHERE s.date = ? AND s.reminded = 0 AND s.q_email IS NOT NULL
               ORDER BY w.time''',
            (reminder_date,)
        ).fetchall()

    sent_count = 0
    for signup in signups:
        if send_q_reminder(dict(signup)):
            # Mark as reminded
            models.update_signup(signup['id'], reminded=True)
            sent_count += 1

    print(f"Sent {sent_count} reminder emails for {reminder_date}")
    return sent_count


if __name__ == '__main__':
    # Run reminder batch when executed directly
    send_reminders_batch()
