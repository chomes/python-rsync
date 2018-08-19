# Author chomes@github
# E-mail function script V1.2
# Importing functions
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
import email.encoders
import email.header
import configparser


# Separate functions created for sending emails to make it more modular and to allow multiple functions to re-use it.
def send_mail_unsecure(username, passwd, from_addr, to_addr, port, smtp_server, email_msg):
    server = smtplib.SMTP(smtp_server, port)
    server.login(username, passwd)
    server.sendmail(from_addr, to_addr, email_msg)
    server.quit()


def send_mail_unsecure_no_auth(from_addr, to_addr, port, smtp_server, email_msg):
    server = smtplib.SMTP(smtp_server, port)
    server.sendmail(from_addr, to_addr, email_msg)
    server.quit()


def send_mail_secure(username, passwd, from_addr, to_addr, ssl_tls, port, smtp_server, email_msg):
    if ssl_tls == "ssl":
        server = smtplib.SMTP_SSL(smtp_server, port)
    else:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
    server.login(username, passwd)
    server.sendmail(from_addr, to_addr, email_msg)
    server.quit()


def send_mail_secure_no_auth(from_addr, to_addr, ssl_tls, port, smtp_server, email_msg):
    if ssl_tls == "ssl":
        server = smtplib.SMTP_SSL(smtp_server, port)
    else:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
    server.sendmail(from_addr, to_addr, email_msg)
    server.quit()


# Function for sending email for starting backup
def backup_start():
    config = configparser.ConfigParser()
    config.read('email_config.ini')
    # Begin importing variables
    username = config.get("server_details", "username")
    passwd = config.get("server_details", "password")
    from_addr = config.get("server_details", "from_addr")
    to_addr = config.get("server_details", "to_addr")
    port = config.get("server_details", "port")
    smtp_server = config.get("server_details", "server")
    ssl_tls = config.get("server_details", "ssl_tls")
    # If value doesn't exit for port, default to 25 for sending mail else it will make the value of port an integer
    port = 25 if not port else int(port)
    # Creating multipart message to send
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = "Backup commencing"
    msg['Message-ID'] = email.header.Header(email.utils.make_msgid())
    body = "The backup is now taking place, we will send you a notification once it's done"
    msg.attach(MIMEText(body, 'plain'))
    email_msg = msg.as_string()
    # If statement based on config file conditions will send email secure/unsecure with/without auth
    if config.get("server_details", "auth") == "no":
        if config.get("server_details", "secure") == "no":
            send_mail_unsecure_no_auth(from_addr, to_addr, port, smtp_server, email_msg)
        else:
            send_mail_secure_no_auth(from_addr, to_addr, ssl_tls, port, smtp_server, email_msg)
    else:
        if config.get("server_details", "secure") == "no":
            send_mail_unsecure(username, passwd, from_addr, to_addr, port, smtp_server, email_msg)
        else:
            send_mail_secure(username, passwd, from_addr, to_addr, ssl_tls, port, smtp_server, email_msg)


# Function for sending email for completion variable for if log_loc = None then will not attach email
def backup_completed(log_loc):
    config = configparser.ConfigParser()
    config.read('email_config.ini')
    # Importing variables
    username = config.get("server_details", "username")
    passwd = config.get("server_details", "password")
    from_addr = config.get("server_details", "from_addr")
    to_addr = config.get("server_details", "to_addr")
    port = config.get("server_details", "port")
    smtp_server = config.get("server_details", "server")
    ssl_tls = config.get("server_details", "ssl_tls")
    # If value doesn't exit for port, default to 25 for sending mail else it will make the value of port an integer
    port = 25 if not port else int(port)
    # Creating multipart message to send
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = "Backup is complete"
    msg['Message-ID'] = email.header.Header(email.utils.make_msgid())
    body = "The backup is now done, if you requested logs, they will be attached in this email!"
    msg.attach(MIMEText(body, 'plain'))
    email_msg = msg.as_string()
    if log_loc is not None:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(log_loc, "rb").read())
        email.encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(log_loc))
        msg.attach(part)
    # If statement based on config file conditions will send email secure/unsecure with/without auth
    if config.get("server_details", "auth") == "no":
        if config.get("server_details", "secure") == "no":
            send_mail_unsecure_no_auth(from_addr, to_addr, port, smtp_server, email_msg)
        else:
            send_mail_secure_no_auth(from_addr, to_addr, ssl_tls, port, smtp_server, email_msg)
    else:
        if config.get("server_details", "secure") == "no":
            send_mail_unsecure(username, passwd, from_addr, to_addr, port, smtp_server, email_msg)
        else:
            send_mail_secure(username, passwd, from_addr, to_addr, ssl_tls, port, smtp_server, email_msg)


# Function for sending email for work in progress
def backup_in_progress():
    config = configparser.ConfigParser()
    config.read('email_config.ini')
    # Importing variables
    username = config.get("server_details", "username")
    passwd = config.get("server_details", "password")
    from_addr = config.get("server_details", "from_addr")
    to_addr = config.get("server_details", "to_addr")
    port = config.get("server_details", "port")
    smtp_server = config.get("server_details", "server")
    ssl_tls = config.get("server_details", "ssl_tls")
    # If value doesn't exit for port, default to 25 for sending mail else it will make the value of port an integer
    port = 25 if not port else int(port)
    # Creating multipart message to send
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = "Backup is in progress"
    msg['Message-ID'] = email.header.Header(email.utils.make_msgid())
    body = "The backup is in progress, please wait for completion before continuing"
    msg.attach(MIMEText(body, 'plain'))
    email_msg = msg.as_string()
    # If statement based on config file conditions will send email secure/unsecure with/without auth
    if config.get("server_details", "auth") == "no":
        if config.get("server_details", "secure") == "no":
            send_mail_unsecure_no_auth(from_addr, to_addr, port, smtp_server, email_msg)
        else:
            send_mail_secure_no_auth(from_addr, to_addr, ssl_tls, port, smtp_server, email_msg)
    else:
        if config.get("server_details", "secure") == "no":
            send_mail_unsecure(username, passwd, from_addr, to_addr, port, smtp_server, email_msg)
        else:
            send_mail_secure(username, passwd, from_addr, to_addr, ssl_tls, port, smtp_server, email_msg)
