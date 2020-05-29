# Author chomes@github
# E-mail function script V1.2
# Importing functions
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from email.header import Header
import email.utils
from configparser import ConfigParser


class EmailClient:
    """
    EmailClient class is used to manage email content for sending emails for notifications
    """
    def __init__(self, config: str):
        """
        the __init__ intialises the class and requires one parameter to operate
        :param config: The config can take several arguments but only requires a few:
        * email_server - Name of the mail server you will be using
        * port - Leave this blank if it's 25
        * to_addr - The email address it's going to
        * from_addr - The email address it's coming from
        Non required vars but should be added if you need it:
        - security - set this to ssl or tls if you use it otherwise leave blank
        - auth - set to yes and fill in the following
        - username - username required to send emails
        - password - password required to send emails
        """
        conf = ConfigParser()
        conf.read(config)
        __email_dict: dict = {key: value for item in conf.sections() for key, value in conf.items(item)}
        self.__mail_server: str = __email_dict["server"]
        self.__port: int = 25 if not __email_dict["port"] else int(__email_dict["port"])
        self.__auth: str = None if not __email_dict["auth"] else __email_dict["auth"]
        self.__security: str = None if not __email_dict["security"] else __email_dict["security"]
        self.__auth_user: str = __email_dict["username"]
        self.__auth_password: str = __email_dict["password"]
        self.__to_addr: str = __email_dict["to_addr"]
        self.__from_addr: str = __email_dict["from_addr"]
        self.__msgid: Header = Header(email.utils.make_msgid(domain=self.__from_addr.rsplit("@")[-1]))

    # Method for sending emails
    def send_mail(self, msg, auth=None, security=None):
        """
        Method used to send emails out.
        :param msg: Use the self.msg composer in the parameter field for this
        :param auth: If it doesn't require authentication leave this blank
        :param security: if this doesn't require security leave this blank
        :return: message if successful or unsuccessful response with a return value of the server object
        """
        # Checking for security
        if security == "ssl":
            __smtp_client: smtplib = smtplib.SMTP_SSL(self.__mail_server, self.__port)
        elif security == "tls":
            __smtp_client: smtplib = smtplib.SMTP(self.__mail_server, self.__port)
            __smtp_client.starttls()
        else:
            __smtp_client: smtplib = smtplib.SMTP(self.__mail_server, self.__port)
        # Checking for authentication
        if auth:
            __smtp_client.login(self.__auth_user, self.__auth_password)
        __smtp_client.send_message(msg, self.__from_addr, self.__to_addr)
        __smtp_client.quit()
        print("Email sent")

    # Method for composing email message
    def compose_message(self, action: str, logs=None) -> str:
        """
        Method is used to compose message to send emails out
        :param action: This is three things: start, stop, running
        :param logs: Set to none by default, otherwise this is the location of the logs
        :return: composed mime message
        """
        msg: MIMEMultipart = MIMEMultipart()
        msg['From']: str = self.__from_addr
        msg['To']: str = self.__to_addr
        body: str = str()
        if action == "start":
            msg['Subject']: str = "Backup commencing"
            body: str = "The backup is now taking place, we will send you a notification once it's done"
        elif action == "running":
            msg['Subject']: str = "Running"
            body: str = "The previous backup is still running " \
                        "so you can't run another, we'll notify you when it's finished"
        elif action == "stop":
            msg['Subject']: str = "Backup finished"
            if logs:
                part: MIMEBase = MIMEBase('application', "octet-stream")
                with open(logs, "rb") as file:
                    part.set_payload(file.read())
                    encode_base64(part)
                    part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(logs))
                    msg.attach(part)
                body: str = "The backup is now completed, you can view the " \
                            "logs of the backup which is attacked in the email"
            else:
                body: str = "The backup is now completed"
        msg['Message-ID']: Header = self.__msgid
        msg.attach(MIMEText(body, 'plain'))
        email_msg: str = msg.as_string()
        return email_msg
