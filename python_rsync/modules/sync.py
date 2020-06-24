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
    def __init__(self, sync_config: str or None, username: str or None, ssh_pass: str or None,
                 remote_server: str or None, ssh_key: str or None, email_config: str or None,
                 source: str or None, destination: str or None, log_path: str or None,
                 log_level: str or None, auto_trust: bool or None, server_port: int or None):
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
        self.logs: Logger or None = None
        try:
            if data["log_level"] or log_level:
                if data["log_location"] or log_path:
                    self.logs: Logger = Logger(log_path=Path(rf"{data['log_location']}") if not log_path
                                               else Path(rf"{log_path}"),
                                               log_level=data["log_level"] if not log_level else log_level)
                else:
                    self.logs: Logger = Logger(log_path=None,
                                               log_level=data["log_level"] if not log_level else log_level)
        except KeyError:
            pass
        self.backup_type: str = config.sections()[0]
        self.sor: Union[str, Path] = Path(rf"{data['source']}") if not source else Path(rf"{source}")
        self.des: Union[str, Path] = Path(rf"{data['des']}") if not destination else Path(rf"{destination}")
        try:
            self.ssh_key: Union[str, Path] = Path(rf"{data['ssh_key']}") if not ssh_key else Path(rf"{ssh_key}")
        except KeyError:
            pass
        try:
            self.ssh_pass: str = data["pass_phrase"] if not ssh_pass else ssh_pass
        except KeyError:
            pass
        try:
            self.username: str = data["username"] if not username else username
        except KeyError:
            pass
        self.auto_trust: bool = False if not data["auto_trust"] or not auto_trust else True
        try:
            self.server_port: int = 22 if not data["server_port"] or not server_port\
                else int(data["server_port"]) or int(server_port)
        except KeyError:
            pass
        try:
            self.server: str = data["remote_server"] if not remote_server else remote_server
        except KeyError:
            pass
        self.lock: str = "backup"
        self.email: EmailClient = None if not data["email"] or email_config\
            else EmailClient(config=Path(rf"{data['email']}" if not email_config else Path(rf"{email_config}")))

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
        elif self.backup_type == "RemRem":
            return RemoteDirectory(directory=self.sor, ssh_key=self.ssh_key, logger=self.logs, ssh_pass=self.ssh_pass,
                                   server=self.server, server_port=self.server_port, username=self.username,
                                   auto_trust=self.auto_trust), \
                   RemoteDirectory(directory=self.sor, ssh_key=self.ssh_key, logger=self.logs, ssh_pass=self.ssh_pass,
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
        for file in enumerate(pruned_files):
            file[1]["object"].delete_file()

        if len(pruned_files) == 0:
            for directory in pruned_folders:
                directory["object"].rmdir()

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
