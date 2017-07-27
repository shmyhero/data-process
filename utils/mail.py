import smtplib
from email.mime.text import MIMEText


def sendmail(smtp_server, sender, sender_password, receiver, subject, content_file):
    fp = open(content_file, 'rb')
    msg = MIMEText(fp.read())
    fp.close()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver
    s = smtplib.SMTP()
    s.connect(smtp_server)
    s.login(sender, sender_password)
    s.sendmail(sender, [receiver], msg.as_string())
    s.close()
