from paramiko.client import SSHClient, AutoAddPolicy
from typing import Union
from pathlib import Path
from paramiko.sftp_client import SFTPClient
from python_rsync.modules.local_file import LocalFile
from time import ctime
from python_rsync.modules.logger import Logger


class RemoteFile:
    def __init__(self, file: Path, ssh_key: Path, logger: Logger or None, ssh_pass: None or str,
                 server: str, server_port: int or None, username: str,
                 auto_trust: bool = False,
                 active_ssh: SSHClient or None = None):
        """
        A way to manipulate remote files from a server to manage them
        :param file: Path of the file on the remote server
        :param ssh_key: ssh key used to connect to the server
        :param ssh_pass: pass phrase for the ssh key
        :param server: server to connect to
        :param server_port: ssh port of the server
        :param logger: Parse in logger for file
        :param username: username to remote to
        :param auto_trust: If the host isn't trusted
        """
        self.ssh_client: SSHClient = active_ssh if active_ssh else SSHClient()
        self.__auto_trust: bool = auto_trust
        if auto_trust:
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        else:
            self.ssh_client.load_system_host_keys()
        if logger:
            self.logger: Logger = logger
        else:
            self.logger: None = None
        self.__ssh_key: Path = ssh_key
        self.__ssh_password: str = ssh_pass
        self.__ssh_port: int = 22 if not server_port else int(server_port)
        self.__ssh_server: str = server
        self.__ssh_username: str = username
        self.file: Union[str, Path] = file
        self.sftp_client: None or SFTPClient = None

    def __repr__(self):
        return f"Remote file {self.file}"

    def __str__(self):
        return rf"{self.file}"

    def check_ssh_connection(self) -> True or False:
        """
        Method used to check if the session is active or not
        :return:
        """
        try:
            transport = self.ssh_client.get_transport()
            if transport.send_ignore():
                return True
            else:
                return False
        except EOFError:
            return False
        except AttributeError:
            return False

    def ssh_connect(self):
        """
        Method used to set up a connection to ssh server
        :return: Updates the client attribute with a connected client
        """
        self.ssh_client.connect(hostname=self.__ssh_server, port=self.__ssh_port,
                                username=self.__ssh_username, passphrase=self.__ssh_password,
                                key_filename=self.__ssh_key.__str__())

    def sftp_connect(self):
        """
        Method used to set up a sftp connection
        :return: Updates the sftp connection
        """
        self.ssh_connect()
        self.sftp_client: SFTPClient = self.ssh_client.open_sftp()

    def md5_hash(self, copy: bool = False) -> str:
        """
        Method used to grab the md5sum of the remote file, used only with compare_md5
        :param copy: Boolean, set to True if you plan to copy the file after as to not close the ssh connection
        :return: md5 value of file
        """
        if not self.check_ssh_connection():
            self.ssh_connect()
        stdin, stdout, stderr = self.ssh_client.exec_command(f"md5sum {self.__str__()}")
        if not copy:
            self.ssh_client.close()
        return stdout.read().decode().split(" ")[0]

    def modified_time(self) -> ctime:
        """
        Method used to grab modified time of the file
        :return: Modified date of the file
        """
        if not self.check_ssh_connection():
            self.sftp_connect()
        else:
            self.sftp_client: SFTPClient = self.ssh_client.open_sftp()
        modified_time = ctime(self.sftp_client.file(self.__str__()).stat().st_mtime)
        self.sftp_client.close()
        self.ssh_client.close()
        return modified_time

    def compare_md5(self, md5sum: str, copy: bool = False) -> True or False:
        """
        Method used to compare md5sum of the local and remote file to see if they are the same
        :param copy: Boolean, set to True if you plan to copy the file after as to not close the ssh connection
        :param md5sum: Local md5sum value
        :return:
        """
        if self.md5_hash(copy=copy) == md5sum:
            return True
        else:
            return False

    def transfer_method(self, local_path: LocalFile, action: str) -> True or Exception:
        """
        Method used to run the try methods for copying files remotely or locally
        :param local_path: Local file copied
        :param action: local or remote - Use this to specify if it's a remote or local copy
        :return: True or exception
        """
        try:
            if action == "local":
                self.sftp_client.put(remotepath=self.__str__(), localpath=local_path.__str__())
                if self.logger:
                    self.logger.info(f"Local file: {local_path.__str__()} was copied to {self.__str__()}")
            elif action == "remote":
                self.sftp_client.get(localpath=local_path.__str__(), remotepath=self.__str__())
                if self.logger:
                    self.logger.info(f"Remote file: {self.__str__()} was copied locally to {local_path.__str__()}")
            self.sftp_client.close()
            self.ssh_client.close()
            return True
        except FileNotFoundError as e:
            if self.logger:
                self.logger.warning(f" File {self.file} does not exist, please try again")
            self.sftp_client.close()
            self.ssh_client.close()
            return e
        except PermissionError as e:
            if self.logger:
                self.logger.warning(f"You don't have access to {local_path}, please try again")
            self.sftp_client.close()
            self.ssh_client.close()
            return e
        except IsADirectoryError as e:
            if self.logger:
                self.logger.warning(f"{local_path} is a directory and not a file, please try again")
            self.sftp_client.close()
            self.ssh_client.close()
            return e

    def local_to_remote_copy(self, local_path: LocalFile) -> True or Exception:
        """
        Method used to copy file from local to remote
        :param local_path: Local location of the file
        :return: File will be copied over
        """
        if not self.check_ssh_connection():
            self.sftp_connect()
        else:
            self.sftp_client: SFTPClient = self.ssh_client.open_sftp()
        if self.file_exists(copy=True):
            if not self.compare_md5(local_path.md5_hash(), copy=True):
                return self.transfer_method(local_path=local_path, action="local")
            else:
                if self.logger:
                    self.logger.info("File has been copied already")
                return FileExistsError
        else:
            return self.transfer_method(local_path=local_path, action="local")

    def remote_to_local_copy(self, local_path: LocalFile) -> True or Exception:
        """
        Method used to copy the remote file to the local machine
        :param local_path: Local location of the new file
        :return: File will be copied over
        """
        if not self.check_ssh_connection():
            self.sftp_connect()
        else:
            self.sftp_client: SFTPClient = self.ssh_client.open_sftp()
        if local_path.file.exists():
            if not self.compare_md5(local_path.md5_hash(), copy=True):
                return self.transfer_method(local_path=local_path, action="remote")
            else:
                if self.logger:
                    self.logger.info("File has been copied already")
                return FileExistsError
        else:
            return self.transfer_method(local_path=local_path, action="remote")

    def file_exists(self, copy: bool = False) -> True or False:
        """
        Method used to check if file exists
        :return: True or False
        """
        if not self.check_ssh_connection():
            self.sftp_connect()
        else:
            self.sftp_client: SFTPClient = self.ssh_client.open_sftp()
        try:
            self.sftp_client.stat(self.__str__())
            if not copy:
                self.sftp_client.close()
                self.ssh_client.close()
                return True
            else:
                return True
        except FileNotFoundError:
            if self.logger:
                self.logger.warning(f"Can't find {self.file}, check that it exists")
            if not copy:
                self.sftp_client.close()
                self.ssh_client.close()
                return False
            else:
                return False

    def delete_file(self) -> True or Exception:
        if not self.check_ssh_connection():
            self.sftp_connect()
        else:
            self.sftp_client: SFTPClient = self.ssh_client.open_sftp()
        try:
            self.sftp_client.unlink(self.__str__())
            if self.logger:
                self.logger.info(f"File: {self.__str__()} has been deleted")
            self.sftp_client.close()
            self.ssh_client.close()
            return True
        except FileNotFoundError:
            if self.logger:
                self.logger.info(f"File: {self.__str__()} does not exist")
            self.sftp_client.close()
            self.ssh_client.close()
            return FileNotFoundError
        except PermissionError:
            if self.logger:
                self.logger.warning(f"You do not have access to: {self.__str__()}")
            self.sftp_client.close()
            self.ssh_client.close()
            return PermissionError
