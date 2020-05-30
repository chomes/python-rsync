# collect all folders and files
# convert to list
# remote copy entire directory
# remote receive entire directory
# get hash of directory
# get modified date
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko import sftp_client
from mods.remote_file import RemoteFile
from pathlib import Path
from time import ctime
from stat import S_ISDIR
from typing import List, Dict


class RemoteDirectory:
    def __init__(self, directory: str, ssh_key: str, ssh_pass: None or str,
                 server: str, server_port: int or None, username: str,
                 auto_trust: bool = False):
        self.__ssh_client: SSHClient = SSHClient()
        if auto_trust:
            self.__ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        self.__ssh_key: str = ssh_key
        self.__ssh_password: str = ssh_pass
        self.__ssh_port: int = 22 if not server_port else int(server_port)
        self.__ssh_server: str = server
        self.__ssh_username: str = username
        self.directory: str = directory
        self.__ssh_client.connect(hostname=self.__ssh_server, port=self.__ssh_port,
                                  username=self.__ssh_username, passphrase=self.__ssh_password,
                                  key_filename=self.__ssh_key)
        stdin, stdout, stderr = self.__ssh_client.exec_command(f"find {self.directory} -print")
        pre_config: list = stdout.read().decode().split("\n")
        pre_config.pop(-1)
        pre_config.pop(0)
        sftp: sftp_client = self.__ssh_client.open_sftp()
        self.directory_items: List[Dict[str: str, str: RemoteFile or RemoteDirectory, str: str ]] = list()
        for item in pre_config:
            checker = sftp.lstat(item)
            if S_ISDIR(checker):
                self.directory_items.append({"name": Path(item).name,
                                             "object": RemoteDirectory(directory=item,
                                                                       ssh_key=self.__ssh_key,
                                                                       ssh_pass=self.__ssh_password,
                                                                       server_port=self.__ssh_port,
                                                                       server=self.__ssh_server,
                                                                       username=self.__ssh_username,
                                                                       auto_trust=auto_trust),
                                             "type": "directory"})
            else:
                self.directory_items.append({"name": Path(item).name,
                                             "object": RemoteFile(file=item,
                                                                  ssh_key=self.__ssh_key,
                                                                  ssh_pass=self.__ssh_password,
                                                                  server_port=self.__ssh_port,
                                                                  server=self.__ssh_server,
                                                                  username=self.__ssh_username,
                                                                  auto_trust=auto_trust),
                                             "type": "file"})
        sftp.close()
        self.__ssh_client.close()
        self.__sftp_client: None or sftp_client = None
