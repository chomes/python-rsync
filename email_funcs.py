# Author chomes@github
# E-mail function script V1.0
# Importing functions
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser

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


def backup_start():
    config = configparser.ConfigParser()
    config.read('email_config.ini')
    username = config.get("server_details", "username")
    passwd = config.get("server_details", "password")
    from_addr = config.get("server_details", "from_addr")
    to_addr = config.get("server_details", "to_addr")
    port = config.get("server_details", "port")
    smtp_server = config.get("server_details", "server")
    ssl_tls = config.get("server_details", "ssl_tls")
    if not port:
        port = 25
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = "Backup commencing"
    body = "The backup is now taking place, we will send you a notification once it's done"
    msg.attach(MIMEText(body, 'plain'))
    email_msg = msg.as_string()
    if config.get("server_details", "auth") == "no":
        if config.get("server_details", "secure") == "no":
            send_mail_unsecure_no_auth(from_addr, to_addr, port, smtp_server, email_msg)
        else:
            send_mail_secure_no_auth(from_addr, to_addr, port, ssl_tls, smtp_server, email_msg)
    else:
        if config.get("server_details", "secure") == "no":
            send_mail_unsecure(username, passwd, from_addr, to_addr, port, smtp_server, email_msg)
        else:
            send_mail_secure(username, passwd, from_addr, to_addr, port, ssl_tls, smtp_server, email_msg)


def backup_completed():
    config = configparser.ConfigParser()
    config.read('email_config.ini')
    username = config.get("server_details", "username")
    passwd = config.get("server_details", "password")
    from_addr = config.get("server_details", "from_addr")
    to_addr = config.get("server_details", "to_addr")
    port = config.get("server_details", "port")
    smtp_server = config.get("server_details", "server")
    ssl_tls = config.get("server_details", "ssl_tls")
    if not port:
        port = 25
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = "Backup commencing"
    body = "The backup is now done, the logs are on the server in the folder of the script"
    msg.attach(MIMEText(body, 'plain'))
    email_msg = msg.as_string()
    if config.get("server_details", "auth") == "no":
        if config.get("server_details", "secure") == "no":
            send_mail_unsecure_no_auth(from_addr, to_addr, port, smtp_server, email_msg)
        else:
            send_mail_secure_no_auth(from_addr, to_addr, port, ssl_tls, smtp_server, email_msg)
    else:
        if config.get("server_details", "secure") == "no":
            send_mail_unsecure(username, passwd, from_addr, to_addr, port, smtp_server, email_msg)
        else:
            send_mail_secure(username, passwd, from_addr, to_addr, port, ssl_tls, smtp_server, email_msg)