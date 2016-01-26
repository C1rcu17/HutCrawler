from smtplib import SMTP_SSL
from email.mime.text import MIMEText


class Server(object):
    def __init__(self, server, port, username, password, name, email):
        self.server = server
        self.use_ssl = True
        self.port = port
        self.username = username
        self.password = password
        self.name = name
        self.email = email

    def send_email(self, destination, subject, body):
        with SMTP_SSL(host=self.server, port=self.port) as smtp:
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = '{} <{}>'.format(self.name, self.email)
            msg['To'] = destination
            smtp.login(self.username, self.password)
            smtp.send_message(msg)
