#!/usr/bin/env python3
# Author:chomes@github
# Defining functions
from python_rsync.modules.local_dir import LocalDirectory
from python_rsync.modules.remote_dir import RemoteDirectory
from typing import Union, List
from pathlib import Path
from configparser import ConfigParser
from python_rsync.modules.email import EmailClient
from python_rsync.modules.logger import Logger


class RsyncClient:
    """
    Class for the module of rsync
    """
    def __init__(self, sync_config: str or None = None, username: str or None = None, ssh_pass: str or None = None,
                 remote_server: str or None = None, ssh_key: str or None = None, email_config: str or None = None,
                 source: str or None = None, destination: str or None = None, log_path: str or None = None,
                 log_level: str = "info", auto_trust: bool = False, server_port: int or None = None,
                 backup_type: str or None = None):
        """
        Init for creating the class
        :param sync_config: This is a config file that takes a list of arguments:
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
        data: dict = dict()
        if sync_config:
            config.read(Path(rf"{sync_config}"))
            data: dict = {key: value for section in config.sections() for key, value in config.items(section)}
        try:
            self.logger: Logger = Logger(log_path=None, log_level=data["log_level"])
        except KeyError:
            self.logger: Logger = Logger(log_path=None, log_level=log_level)

        try:
            if data["log_location"]:
                self.logger: Logger = Logger(log_path=Path(rf"{data['log_location']}"),
                                             log_level=data["log_level"])
        except KeyError:
            if log_path:
                self.logger: Logger = Logger(log_path=Path(rf"{log_path}"), log_level=log_level)
        try:
            self.backup_type: str = data["backup_type"]
        except KeyError:
            self.backup_type: str = backup_type

        try:
            self.sor: Union[str, Path] = Path(rf"{data['source']}")
        except KeyError:
            self.sor: Union[str, Path] = Path(rf"{source}")

        try:
            self.des: Union[str, Path] = Path(rf"{data['des']}")
        except KeyError:
            self.des: Union[str, Path] = Path(rf"{destination}")

        try:
            self.ssh_key: Union[str, Path] or None = Path(rf"{data['ssh_key']}") if data["ssh_key"] else None
        except KeyError:
            self.ssh_key: Union[str, Path] or None = Path(rf"{ssh_key}") if ssh_key else None

        try:
            self.ssh_pass: str or None = data["pass_phrase"] if data["pass_phrase"] else None
        except KeyError:
            self.ssh_pass: str or None = ssh_pass if ssh_pass else None
        try:
            self.username: str or None = data["username"] if data["username"] else None
        except KeyError:
            self.username: str or None = username if username else None
        try:
            self.auto_trust: bool = False if not data["auto_trust"] else True
        except KeyError:
            self.auto_trust: bool = False if not auto_trust else True
        try:
            self.server_port: int = 22 if not data["server_port"] else int(data["server_port"])
        except KeyError:
            self.server_port: int = 22 if not server_port else int(server_port)
        try:
            self.server: str or None = data["remote_server"] if data["remote_server"] else None
        except KeyError:
            self.server: str or None = remote_server if remote_server else None
        self.lock: str = "backup"
        try:
            self.email: EmailClient or None = None if not data["email"] \
                else EmailClient(config=Path(rf"{data['email']}"))
        except KeyError:
            self.email: EmailClient or None = None if not email_config else EmailClient(config=Path(rf"{email_config}"))

    def sor_des_generator(self) -> LocalDirectory or RemoteDirectory:
        if self.backup_type == "Local":
            return LocalDirectory(location=self.sor, logger=self.logger), LocalDirectory(location=self.des,
                                                                                         logger=self.logger)
        elif self.backup_type == "LoRem":
            return LocalDirectory(location=self.sor, logger=self.logger), RemoteDirectory(directory=self.des,
                                                                                          ssh_key=self.ssh_key,
                                                                                          logger=self.logger,
                                                                                          ssh_pass=self.ssh_pass,
                                                                                          server=self.server,
                                                                                          server_port=self.server_port,
                                                                                          username=self.username,
                                                                                          auto_trust=self.auto_trust)
        elif self.backup_type == "RemLo":
            return RemoteDirectory(directory=self.sor, ssh_key=self.ssh_key, logger=self.logger, ssh_pass=self.ssh_pass,
                                   server=self.server, server_port=self.server_port, username=self.username,
                                   auto_trust=self.auto_trust), LocalDirectory(location=self.des, logger=self.logger)
        elif self.backup_type == "RemRem":
            return RemoteDirectory(directory=self.sor, ssh_key=self.ssh_key, logger=self.logger, ssh_pass=self.ssh_pass,
                                   server=self.server, server_port=self.server_port, username=self.username,
                                   auto_trust=self.auto_trust), \
                   RemoteDirectory(directory=self.sor, ssh_key=self.ssh_key, logger=self.logger, ssh_pass=self.ssh_pass,
                                   server=self.server, server_port=self.server_port, username=self.username,
                                   auto_trust=self.auto_trust)

    # Method for remote sync
    def remote_sync(self) -> True or False:
        """
        Run a copy from remote to local directory
        :return: Result of action
        """
        if self.email:
            self.email.compose_message(action="start")
        self.sor, self.des = self.sor_des_generator()
        if self.backup_type == "RemLo":
            sync = self.sor.remote_to_local(destination=self.des)
            if sync:
                if self.email:
                    self.email.compose_message(action="stop")
                return True
            else:
                if self.email:
                    self.email.compose_message(action="stop")
                return False
        elif self.backup_type == "LoRem":
            sync = self.des.local_to_remote(source=self.sor)
            if sync:
                if self.email:
                    self.email.compose_message(action="stop")
                return True
            else:
                if self.email:
                    self.email.compose_message(action="stop")
                return False

    def mirror_prune(self) -> True or False:
        """
        When mirror sync is chosen, this method will prune the
        :return: Success or Failure
        """
        pruned_folders: List[dict] = list()
        pruned_files: List[dict] = list()
        self.sor, self.des = self.sor_des_generator()
        for item in self.des.directory_items:
            for checker in self.sor.directory_items:
                if item["name"] == checker["name"]:
                    if item["type"] == "directory":
                        break
                    elif item["object"].compare_md5(checker["object"].md5_hash()):
                        break
            else:
                if item["type"] == "directory":
                    pruned_folders.append(item)
                elif item["type"] == "file":
                    pruned_files.append(item)
        pruned_folders.reverse()
        confirmed_files: list = list()
        self.logger.info(f"Deleting {pruned_files}")
        for file in pruned_files:
            file["object"].delete_file()
            confirmed_files.append(file)

        confirmed_folders: list = list()
        if len(confirmed_files) == len(pruned_files):
            self.logger.info(f"Deleting {pruned_folders}")
            for directory in pruned_folders:
                directory["object"].rmdir()
                confirmed_folders.append(directory)
        elif len(pruned_files) > len(confirmed_files):
            self.logger.warning("Files still exist, exiting")

        if len(confirmed_folders) == pruned_folders:
            self.logger.info(f"{self.des} is pruned and ready to sync")
        elif len(pruned_folders) > len(confirmed_folders):
            self.logger.warning("Not all directories from destination could be deleted, please troubleshoot")

    def local_sync(self) -> True or False:
        """
        Run a local dir copy to local
        :return: Result of action
        """
        if self.email:
            self.email.compose_message(action="start")
        self.sor, self.des = self.sor_des_generator()
        if self.des.directory_exists():
            sync: True or Exception = self.sor.local_sync_dir(self.des)
        else:
            sync: True or Exception = self.sor.local_copy_dir(self.des)
        if sync:
            if self.email:
                self.email.compose_message(action="stop")
            return True
        else:
            if self.email:
                self.email.compose_message(action="stop")
            return False
