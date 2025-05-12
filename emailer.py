import smtplib
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

all_dates = []
next_week = date.today() + timedelta(days=7)
next_week_formatted = next_week.strftime("%B %d")
three_days = date.today() + timedelta(days=3)
three_days_formatted = three_days.strftime("%B %d")
if date.today().weekday() == 6:
    meeting_date = next_week_formatted
    reminder = f"""Hi all,

Here's the week-ahead reminder of our next Circus Guild meeting on {meeting_date}.

Per usual, if you have any agenda items to add you can do so in the description field of the Google Calendar event. If you don't want a proposal subject to a ten-day waiting period presuming it passes this Sunday, then please submit it to the group in writing by this upcoming Thursday.

Also per usual, if you need to attend the event virtually just let us know.

RH
"""
if date.today().weekday() == 3:
    meeting_date = three_days_formatted
    reminder = f"""Dear BCG,

Here is your additional reminder for the upcoming Guild meeting on {meeting_date} at 5 PM.

If you intend to pass any proposals without a ten-day waiting period, please submit them to the Guild by writing by end of day today.
"""

with open('sender_email.txt', 'r') as file:
    email_address = file.read().strip()

with open('email_password.txt', 'r') as file:
    email_password = file.read().strip()

with open('target_email.txt', 'r') as file:
    target_email = file.read().strip()

# Email setup
def send_email(recipient_email, subject, body):
    # Create the email content
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    # Attach the email body
    msg.attach(MIMEText(body.strip(), 'plain'))
    
    try:
        # Connect to the Dreamhost SMTP server
        with smtplib.SMTP_SSL('smtp.dreamhost.com', 465) as server:
            server.login(email_address, email_password)
            # Send the email
            server.sendmail(email_address, recipient_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Example usage
# email_subject = "BCG meeting email reminder: " + meeting_date
send_email(target_email, ("BCG meeting email reminder: " + meeting_date), reminder)