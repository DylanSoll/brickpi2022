import smtplib, ssl
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase


class EmailInterface():
    def __init__(self, sender, password, email_smtp, port = 587):
        """Creates email interface to send emails

        Args:
            sender (str): Users email
            password (str): Users password
            email_smtp (str): The mail smtp used to send emails
            port (int, optional): Port to send email from. Defaults to 587.
        """        
        self.email_sender = sender #converts all details to be used throughout class
        self.email_password = password
        self.port = port
        self.email_smtp = email_smtp
        self.context=ssl.create_default_context() #uses ssl library to encrypt email attachment
        self.msg = ""
        return
    
    def load_message(self, receiver, subject, message):
        """Creates message for email

        Args:
            receiver (str): Receiver email address
            subject (str): Subject of the email
            message (str): Email body
        """        
        self.msg = MIMEMultipart() #creates an email using MIMEMultipart
        self.receiver = receiver 
        self.msg.attach(MIMEText(message, 'html')) #attaches message to email
        self.msg["Subject"] = subject #declares subject
        self.msg["From"] = self.email_sender #declares sender
        self.msg["To"] = receiver #declares receiver
        return


    def attach_file(self, filename, file_title = False):
        """Attaches a file to the email

        Args:
            filename (str): The location of the file
            file_title (bool or str, optional): Name for the file. Defaults to False.
        """        
        attachment = open(filename, 'rb') #opens attachment from location
        payload = MIMEBase('application', 'octet-stream') #create a payload to attach file to
        payload.set_payload(attachment.read()) #sets payload as file contents
        encoders.encode_base64(payload) #encodes payload
        if not file_title: #if file title is not stated
            file_title = filename.split('/')[-1] #uses end of filename
        payload.add_header('Content-Disposition', 'attachment; filename='+file_title)
        #adds a header to the payload, including file title
        self.msg.attach(payload) #attaches attachment to email
        return 


    def send_email(self):
        """Sends the email loaded

        Returns:
            str: Error
        """        
        error = 'No message attached'
        if self.msg != "": #if message is attached
            error = False #no error
            try: #Tries to send email
                with smtplib.SMTP(self.email_smtp, port=self.port) as smtp:
                    smtp.starttls(context=self.context) #encodes email uses ssl
                    try: #tries to login using details provided
                        smtp.login(self.email_sender, self.email_password)
                        try:
                            message = self.msg.as_string() #if successful, attach message
                            smtp.sendmail(self.email_sender, self.receiver, message) #send mail
                            self.msg = "" #clears message
                        except:
                            error = "Failed sending email" #if failed, error with sending email
                    except:
                        error = 'Login failed' #if failed, declare error as login failure                
            except:
                error = 'Email failed'
        return error



