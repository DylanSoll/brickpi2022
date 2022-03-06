import smtplib, ssl
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase


class EmailInterface():
    def __init__(self, sender, password, email_smtp, port = 587):
        self.email_sender = sender
        self.email_password = password
        self.port = port
        self.email_smtp = email_smtp
        self.context=ssl.create_default_context()
        self.msg = ""
        return
    
    def load_message(self, receiver, subject, message):
        self.msg = MIMEMultipart()
        self.receiver = receiver
        self.msg.attach(MIMEText(message, 'html'))
        self.msg["Subject"] = subject
        self.msg["From"] = self.email_sender
        self.msg["To"] = receiver
        return


    def attach_file(self, filename, file_title = False):
        attachment = open(filename, 'rb')
        payload = MIMEBase('application', 'octet-stream')
        payload.set_payload(attachment.read())
        encoders.encode_base64(payload)
        if not file_title:
            file_title = filename
        payload.add_header('Content-Disposition', f'attachment; filename={file_title}')
        self.msg.attach(payload)
        return 


    def send_email(self):
        error = True
        if self.msg != "":
            with smtplib.SMTP(self.email_smtp, port=self.port) as smtp:
                smtp.starttls(context=self.context)
                smtp.login(self.email_sender, self.email_password)
                message = self.msg.as_string()
                smtp.sendmail(self.email_sender, self.receiver, message)
            self.msg = ""
            error = False
        return error
if __name__ == '__main__':
    email = EmailInterface("verylegitimatebusiness@outlook.com", "Year11DigitalScam#Gen1", "smtp-mail.outlook.com")
    email.load_message('22dylansoll@gmail.com', 'This is another test', '')
    email.attach_file('static\music\8_9_10_MP3_song.mp3')
    email.send_email()