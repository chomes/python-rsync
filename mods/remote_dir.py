# remote copy entire directory
# remote receive entire directory

from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.sftp_client import SFTPClient
from mods.remote_file import RemoteFile
from mods.local_dir import LocalDirectory
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
        sftp: SFTPClient = self.__ssh_client.open_sftp()
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
        self.__sftp_client: SFTPClient or None = None

    def __ssh_connect(self):
        """
        Method used to set up a connection to ssh server
        :return: Updates the client attribute with a connected client
        """
        self.__ssh_client.connect(hostname=self.__ssh_server, port=self.__ssh_port,
                                  username=self.__ssh_username, passphrase=self.__ssh_password,
                                  key_filename=self.__ssh_key)

    def __sftp_connect(self):
        """
        Method used to set up a sftp connection
        :return: Updates the sftp connection
        """
        self.__ssh_connect()
        self.__sftp_client: SFTPClient = self.__ssh_client.open_sftp()

    def md5_hash(self) -> str:
        """
        Method used to grab the md5sum of the remote file, used only with compare_md5
        :return: md5 value of file
        """
        self.__ssh_connect()
        stdin, stdout, stderr = self.__ssh_client.exec_command(f"md5sum {self.directory}")
        self.__ssh_client.close()
        return stdout.read().decode().split(" ")[0]

    def modified_time(self) -> ctime:
        """
        Method used to grab modified time of the file
        :return: Modified date of the file
        """
        self.__sftp_connect()
        modified_time = ctime(self.__sftp_client.file(self.directory).stat().st_mtime)
        self.__sftp_client.close()
        self.__ssh_client.close()
        return modified_time

    def compare_md5(self, md5sum: str) -> True or False:
        """
        Method used to compare md5sum of the local and remote file to see if they are the same
        :param md5sum: Local md5sum value
        :return:
        """
        if self.md5_hash() == md5sum:
            return True
        else:
            return False

    def make_dir(self) -> True or False:
        """
        Create directory
        :return: Created the directory or not
        """
        self.__ssh_connect()
        self.__sftp_connect()
        try:
            self.__sftp_client.mkdir(path=self.directory, mode=0o755)
            self.__sftp_client.close()
            self.__ssh_client.close()
            return True
        except PermissionError:
            print("You do not have access to this area, please try again")
            self.__sftp_client.close()
            self.__ssh_client.close()
            return False
        except OSError:
            print("The directory already exists, this is not needed")
            self.__sftp_client.close()
            self.__ssh_client.close()
            return False

    # destination generator
    # using path replace parent
    # set max replace of parent to the source directory and replace with destination

    def copy_remote_to_local(self, destination: LocalDirectory):
        """
        Copy the remote directories contents to local folder
        :param destination:
        :return:
        """
        if destination.directory.exists():
            pass
        else:
            destination.make_dir()

    def directory_exists(self) -> True or False:
        """
        Method used to check if file exists
        :return: True or False
        """
        self.__sftp_connect()
        try:
            self.__sftp_client.stat(self.directory)
            self.__sftp_client.close()
            self.__ssh_client.close()
            return True
        except FileNotFoundError:
            print(f"Can't find {self.directory}, check that it exists")
            self.__sftp_client.close()
            self.__ssh_client.close()
            return False
