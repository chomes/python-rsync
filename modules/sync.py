#!/usr/bin/env python3
# Author:chomes@github
# Defining functions
from modules.local_dir import LocalDirectory
from modules.remote_dir import RemoteDirectory
from modules.local_file import LocalFile
from modules.remote_file import RemoteFile
from typing import Union
from pathlib import Path
from configparser import ConfigParser
from modules.email import EmailClient
from modules.logger import Logger


class RsyncClient:
    """
    Class for the module of rsync
    """
    def __init__(self, file: Union[str, Path]):
        """
        Init for creating the class
        :param file: This is a config file that takes a list of arguments:
        * source - source folder
        * destination - destination folder
        * log_location - Location of logs, if blank this will be set to none
        * username - username of the remote server
        * server - remote server
        * port - ssh port of remote server
        * log_level - Choose between: debug, info, warning and critical
        * ssh_key - Location of your ssh key
        * pass_phrase - Password of your ssh key
        * email - Path to your email config
        """
        config = ConfigParser()
        config.read(file)
        data = {key: value for section in config.sections() for key, value in config.items(section)}
        self.logs: Logger or None = None if not data["log_location"] else Logger(log_path=Path(data["log_location"]),
                                                                                 log_level=data["log_level"])
        self.backup_type: str = config.sections()[0]
        self.sor: Union[str, Path] = Path(data["source"])
        self.des: Union[str, Path] = Path(data["des"])
        self.ssh_key: Union[str, Path] = Path(data["ssh_key"])
        self.ssh_pass: str = data["pass_phrase"]
        self.username: str = data["username"]
        self.auto_trust: bool = False if not data["autu_trust"] else True
        self.server_port: int = 22 if not data["server_port"] else int(data["server_port"])
        self.server: str = data["remote_server"]
        self.lock: str = "backup"
        self.email: EmailClient = None if not data["email"] else EmailClient(config=Path(data["email"]))

    def sor_des_generator(self) -> LocalDirectory or RemoteDirectory:
        if self.backup_type == "Local":
            return LocalDirectory(location=self.sor, logger=self.logs), LocalDirectory(location=self.des,
                                                                                       logger=self.logs)
        elif self.backup_type == "LoRem":
            return LocalDirectory(location=self.sor, logger=self.logs), RemoteDirectory(directory=self.des,
                                                                                        ssh_key=self.ssh_key,
                                                                                        logger=self.logs,
                                                                                        ssh_pass=self.ssh_pass,
                                                                                        server=self.server,
                                                                                        server_port=self.server_port,
                                                                                        username=self.username,
                                                                                        auto_trust=self.auto_trust)
        elif self.backup_type == "RemLo":
            return RemoteDirectory(directory=self.sor, ssh_key=self.ssh_key, logger=self.logs, ssh_pass=self.ssh_pass,
                                   server=self.server, server_port=self.server_port, username=self.username,
                                   auto_trust=self.auto_trust), LocalDirectory(location=self.des, logger=self.logs)

    # Method for remote sync
    def remote_to_local(self):
        """
        Run a copy from remote to local directory
        :return: Result of action
        """
        if self.email:
            self.email.compose_message(action="start")
        self.sor, self.des = self.sor_des_generator()
        sync = self.sor.remote_to_local(destination=self.des)
