# python script for sending SMTP configuration with Oracle Cloud Infrastructure Email Delivery
import smtplib 
import email.utils
from email.message import EmailMessage
import ssl
import sys


HOST = "smtp.email.uk-london-1.oci.oraclecloud.com"
PORT = 25
USERNAME_SMTP = 'ocid1.user.oc1..aaa[...]me3boaq.tm.com'
PASSWORD_SMTP_FILE = 'send_email.cfg'
SENDER = 'noreply@whatever.com'
SENDERNAME = 'noreply@whatever.com'

RECIPIENT=sys.argv[1].split(',')
SUBJECT = sys.argv[2]
BODY_TEXT = sys.argv[3]
 
# The HTML body of the email.
BODY_HTML = f"""<html>
<head></head>
<body>
  <h1>{SUBJECT}</h1>
  <p>{BODY_TEXT}</p>
</body>
</html>"""

with open(PASSWORD_SMTP_FILE) as f:
    password_smtp = f.readline().strip()

msg = EmailMessage()
msg['Subject'] = SUBJECT
msg['From'] = SENDER
msg['To'] = RECIPIENT

msg.add_alternative(BODY_TEXT, subtype='text')
msg.add_alternative(BODY_HTML, subtype='html')

try: 
    server = smtplib.SMTP(HOST, PORT)
    server.ehlo()
    server.starttls(context=ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=None, capath=None))
    server.ehlo()
    server.login(USERNAME_SMTP, password_smtp)
    server.sendmail(SENDER, RECIPIENT, msg.as_string())
    server.close()

except Exception as e:
    print(f"Error: {e}")
else:
    print("Email successfully sent!")
