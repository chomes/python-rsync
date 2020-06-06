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
from typing import Union
from pathlib import Path
import email.utils
from configparser import ConfigParser


class EmailClient:
    """
    EmailClient class is used to manage email content for sending emails for notifications
    """
    def __init__(self, config: Union[str, Path]):
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
        email_dict: dict = {key: value for item in conf.sections() for key, value in conf.items(item)}
        self.__mail_server: str = email_dict["server"]
        self.__port: int = 25 if not email_dict["port"] else int(email_dict["port"])
        self.__auth: bool = False if not email_dict["auth"] else True
        self.__security: str or None = None if not email_dict["security"] else email_dict["security"]
        self.__auth_user: str or None = None if not email_dict["username"] else email_dict["username"]
        self.__auth_password: str or None = None if not email_dict["password"] else email_dict["password"]
        self.__to_addr: str = email_dict["to_addr"]
        self.__from_addr: str = email_dict["from_addr"]
        self.__msgid: Header = Header(email.utils.make_msgid(domain=self.__from_addr.rsplit("@")[-1]))

    def __str__(self):
        return self.__from_addr

    def __repr__(self):
        return f"Sending from: {self.__to_addr} to: {self.__from_addr}"

    # Method for sending emails
    def send_mail(self, msg: MIMEMultipart):
        """
        Method used to send emails out.
        :param msg: Use the self.msg composer in the parameter field for this
        :return: message if successful or unsuccessful response with a return value of the server object
        """
        # Checking for security
        if self.__security == "ssl":
            smtp_client: smtplib = smtplib.SMTP_SSL(self.__mail_server, self.__port)
        elif self.__security == "tls":
            smtp_client: smtplib = smtplib.SMTP(self.__mail_server, self.__port)
            smtp_client.starttls()
        else:
            smtp_client: smtplib = smtplib.SMTP(self.__mail_server, self.__port)
        # Checking for authentication
        if self.__auth:
            smtp_client.login(self.__auth_user, self.__auth_password)
        smtp_client.send_message(msg, self.__from_addr, self.__to_addr)
        smtp_client.quit()
        print("Email sent")

    # Method for composing email message
    def compose_message(self, action: str, logs: Union[str, Path] or None = None) -> str:
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
                    part.add_header('Content-Disposition', 'attachment', filename=logs.name)
                    msg.attach(part)
                body: str = "The backup is now completed, you can view the " \
                            "logs of the backup which is attacked in the email"
            else:
                body: str = "The backup is now completed"
        msg['Message-ID']: Header = self.__msgid
        msg.attach(MIMEText(body, 'plain'))
        email_msg: str = msg.as_string()
        return email_msg
