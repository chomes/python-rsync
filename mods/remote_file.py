from paramiko.client import SSHClient, AutoAddPolicy
from paramiko import sftp_client
from time import ctime


class RemoteFile:
    def __init__(self, file: str, ssh_key: str, ssh_pass: None or str,
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
        self.file: str = file
        self.__sftp_client: None or sftp_client = None

    def __repr__(self):
        return f"Remote file {self.file}"

    def __str__(self):
        return self.file

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
        self.__sftp_client: sftp_client = self.__ssh_client.open_sftp()

    def md5_hash(self) -> str:
        """
        Method used to grab the md5sum of the remote file, used only with compare_md5
        :return: md5 value of file
        """
        self.__ssh_connect()
        stdin, stdout, stderr = self.__ssh_client.exec_command(f"md5sum {self.file}")
        self.__ssh_client.close()
        return stdout.read().decode().split(" ")[0]

    def modified_time(self) -> ctime:
        """
        Method used to grab modified time of the file
        :return: Modified date of the file
        """
        self.__sftp_connect()
        modified_time = ctime(self.__sftp_client.file(self.file).stat().st_mtime)
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

    def local_to_remote_copy(self, local_path: str) -> True or Exception:
        """
        Method used to copy file from local to remote
        :param local_path: Local location of the file
        :return: File will be copied over
        """
        self.__sftp_connect()
        try:
            self.__sftp_client.put(localpath=local_path, remotepath=self.file)
            self.__sftp_client.close()
            self.__ssh_client.close()
            return True
        except IsADirectoryError as e:
            print(f"{local_path} is a directory, please check again")
            self.__sftp_client.close()
            self.__ssh_client.close()
            return e
        except FileNotFoundError as e:
            print(f"{local_path} does not exist, please check again")
            self.__sftp_client.close()
            self.__ssh_client.close()
            return e
        except PermissionError as e:
            print("Either you don't have access to the local area or the remote, please try again")
            self.__sftp_client.close()
            self.__ssh_client.close()
            return e

    def remote_to_local_copy(self, local_path: str) -> True or Exception:
        """
        Method used to copy the remote file to the local machine
        :param local_path: Local location of the new file
        :return: File will be copied over
        """
        self.__sftp_connect()
        try:
            self.__sftp_client.get(remotepath=self.file, localpath=local_path)
        except FileNotFoundError as e:
            print(f" File {self.file} does not exist, please try again")
            self.__sftp_client.close()
            self.__ssh_client.close()
            return e
        except PermissionError as e:
            print(f"You don't have access to {local_path}, please try again")
            self.__sftp_client.close()
            self.__ssh_client.close()
            return e
        except IsADirectoryError as e:
            print(f"{local_path} is a directory and not a file, please try again")
            self.__sftp_client.close()
            self.__ssh_client.close()
            return e

    def file_exists(self) -> True or False:
        """
        Method used to check if file exists
        :return: True or False
        """
        self.__sftp_connect()
        try:
            self.__sftp_client.stat(self.file)
            self.__sftp_client.close()
            self.__ssh_client.close()
            return True
        except FileNotFoundError:
            print(f"Can't find {self.file}, check that it exists")
            self.__sftp_client.close()
            self.__ssh_client.close()
            return False
