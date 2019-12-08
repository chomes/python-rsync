#!/usr/bin/env python3
# Author:chomes@github
# Defining functions
from subprocess import Popen
from pathlib import Path
from configparser import ConfigParser
from mods.email import EmailClient
import sys


class RsyncClient:
    """
    Class for the module of rsync
    """
    def __init__(self, file):
        """
        Init for creating the class
        :param file: This is a config file that takes a list of arguments:
        * source - source folder
        * destination - destination folder
        * log_location - Location of logs, if blank this will be set to none
        * username - username of the remote server
        * server - remote server
        * port - ssh port of remote server
        """
        config = ConfigParser()
        config.read(file)
        data = {key: value for section in config.sections() for key, value in config.items(section)}
        self.sor = data["source"]
        self.des = data["destination"]
        self.backup_type = config.sections()[0]
        self.logs = None if not data["log_location"] else data["log_location"]
        self.lock = "backup" if not data["lock_name"] else data["lock_name"]
        self.username = None if not data["username"] else data["username"]
        self.server = None if not data["remote_server"] else data["remote_server"]
        self.port = None if not data["server_port"] else data["server_port"]
        self.email = None if not data["email"] else data["email"]

    # Method for installing rsync
    # noinspection PyMethodMayBeStatic
    def install_rsync(self, distro):
        """
        Method for installing rsync
        :param distro: choose, debian, redhat
        :return: Notification of package installed
        """
        if distro == "debian":
            command = "apt install rsync"
            Popen(command, shell=True).wait()
        elif distro == "rhel":
            command = "yum install rsync"
            Popen(command, shell=True).wait()
        print("Package installed")

    # Method for remote sync
    def remote_command(self, action, logs=None):
        """
        Method to run remote rsync
        :param action: What action is required for local or remote
        :param logs: Logs is set to None by default, will allow user to write to log file
        :return: Shell command
        """
        if logs:
            command = None
            if action == "LoRem":
                command = f"rsync -avv {self.sor} " \
                          f"--port={self.port} {self.username}@{self.server}:{self.des} --log-file={logs}"
            elif action == "RemLo":
                command = f"rsync -avv --port={self.port} {self.username}@{self.server}:{self.sor} {self.des}" \
                          f"--log-file={logs}"
            run = Popen(command, shell=True).wait()
            return run
        else:
            command = None
            if action == "LoRem":
                command = f"rsync -avv {self.sor} --port={self.port} {self.username}@{self.server}:{self.des}"
            elif action == "RemLo":
                command = f"rsync -avv --port={self.port} {self.username}@{self.server}:{self.sor} {self.des}"
            run = Popen(command, shell=True).wait()
            return run

    # Method for running locally
    def local_command(self, logs=None):
        """
        Method for running backup locally
        :param logs: Set to None by default, will allow user to write to log file
        :return: shell command
        """
        if logs:
            command = f"rsync -avv {self.sor} {self.des} --log-file={logs}"
            run = Popen(command, shell=True)
            return run
        else:
            command = f"rsync -avv {self.sor} {self.des} --log-file{logs}"
            run = Popen(command, shell=True)
            return run

    # Method for backup composing
    def backup_email(self, logs=None):
        """
        Method used for backing up via email
        :param logs: Set to None if used will attach logs via email
        :return: return back
        """
        ec = EmailClient(self.email)
        start_msg = ec.compose_message("start")
        ec.send_mail(start_msg, ec.auth, ec.security)
        if self.backup_type == "Manual":
            self.local_command(logs)
        else:
            self.remote_command(self.backup_type, logs)
        complete_msg = ec.compose_message("stop", logs)
        ec.send_mail(complete_msg, ec.auth, ec.security)

    def backup(self, logs=None):
        """
        Method used to backup without emails
        :param logs: Logs set to None by default
        :return: backs up the file
        """
        print("Starting backup")
        if self.backup_type == "Manual":
            self.local_command(logs)
        else:
            self.remote_command(self.backup_type, logs)
        print("Backup is complete")

    # Method for running sync
    def run_sync(self, logs=None):
        if Path(self.lock).is_file():
            if self.email:
                ec = EmailClient(self.email)
                msg = ec.compose_message("running", logs)
                ec.send_mail(msg, ec.auth, ec.security)
                sys.exit()
            else:
                print("Backup is still running, please check in later")
                sys.exit()
        else:
            if self.email:
                self.backup_email(logs)
            else:
                self.backup(logs)
