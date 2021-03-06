from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.sftp_client import SFTPClient
from python_rsync.modules.remote_file import RemoteFile
from python_rsync.modules.local_dir import LocalDirectory
from python_rsync.modules.local_file import LocalFile
from typing import Union, List, Dict, Any
from pathlib import Path
from time import ctime
from stat import S_ISDIR
from python_rsync.modules.logger import Logger


class RemoteDirectory:
    def __init__(self, directory: Path, ssh_key: Path, ssh_pass: None or str,
                 server: str, username: str, server_port: int or None = None,
                 auto_trust: bool = False, cascade: bool = True,
                 active_ssh: None or SSHClient = None, logger: Logger or None = None):
        """
        Remote directory allows you to manipulate the files and folders inside of the directory by copying
        them, getting their hash sum or by checking things like modified date
        :param directory: Directory you're targeting remotely
        :param ssh_key: path of your ssh key file locally
        :param ssh_pass: pass phrase of your ssh key
        :param server: FQDN of the server, if a shortname is in your host file, you can use this too.
        :param server_port: port of the server you're connecting to
        :param username: Username on the remote host
        :param auto_trust: If you haven't trusted this host this to True so you don't error out on the ssh connection.
        :param cascade: This will iter through all files and sub directories of this folder, this is set to True
        :param active_ssh: Provide an active ssh client into the directory to reduce slowness of connection
        for the source or destination folder but will auto set it to False for it's sub directories, if
        required the user can use the update_folders method to get all contents from each sub directory.

        IMPORTANT:  If you have a large amount of files, expect this to some time as it does multiple ssh connections
        one at a time #TODO investigate processes to help this
        """
        self.ssh_client: SSHClient = active_ssh if active_ssh else SSHClient()
        self.__auto_trust: bool = auto_trust
        if auto_trust:
            self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        else:
            self.ssh_client.load_system_host_keys()
        self.__ssh_key: Path = ssh_key
        if logger:
            self.logger: Logger = logger
        else:
            self.logger: None = None
        self.__ssh_password: str = ssh_pass
        self.__ssh_port: int = 22 if not server_port else int(server_port)
        self.__ssh_server: str = server
        self.__ssh_username: str = username
        self.directory: Union[str, Path] = directory
        if not active_ssh:
            self.ssh_client.connect(hostname=self.__ssh_server, port=self.__ssh_port,
                                    username=self.__ssh_username, passphrase=self.__ssh_password,
                                    key_filename=self.__ssh_key.__str__())
        sftp: SFTPClient = self.ssh_client.open_sftp()
        try:
            stat = sftp.lstat(self.directory.__str__())
        except FileNotFoundError:
            stat = False
        self.directory_items: List[Dict[str, RemoteFile or RemoteDirectory]] = list()
        if stat and cascade:
            stdin, stdout, stderr = self.ssh_client.exec_command(f"find {self.directory} -print")
            pre_config: list = stdout.read().decode().split("\n")
            pre_config.pop(-1)
            pre_config.pop(0)
            for item in pre_config:
                checker = sftp.lstat(item)
                if S_ISDIR(checker.st_mode):
                    self.directory_items.append({"name": Path(item).name,
                                                 "object": RemoteDirectory(directory=Path(item),
                                                                           ssh_key=self.__ssh_key,
                                                                           ssh_pass=self.__ssh_password,
                                                                           server_port=self.__ssh_port,
                                                                           server=self.__ssh_server,
                                                                           username=self.__ssh_username,
                                                                           auto_trust=self.__auto_trust,
                                                                           cascade=False,
                                                                           active_ssh=self.ssh_client,
                                                                           logger=self.logger),
                                                 "type": "directory"})
                else:
                    self.directory_items.append({"name": Path(item).name,
                                                 "object": RemoteFile(file=Path(item),
                                                                      ssh_key=self.__ssh_key,
                                                                      ssh_pass=self.__ssh_password,
                                                                      server_port=self.__ssh_port,
                                                                      server=self.__ssh_server,
                                                                      username=self.__ssh_username,
                                                                      auto_trust=self.__auto_trust,
                                                                      active_ssh=self.ssh_client,
                                                                      logger=self.logger),
                                                 "type": "file"})
        else:
            pass
        sftp.close()
        self.sftp_client: SFTPClient or None = None

    def __str__(self):
        return rf"{self.directory}"

    def __repr__(self):
        return f"{self.directory} has {len(self.directory_items)} files and folders"

    def ssh_connect(self):
        """
        Method used to set up a connection to ssh server
        :return: Updates the client attribute with a connected client
        """
        self.ssh_client.connect(hostname=self.__ssh_server, port=self.__ssh_port,
                                username=self.__ssh_username, passphrase=self.__ssh_password,
                                key_filename=self.__ssh_key.__str__())

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

    def sftp_connect(self):
        """
        Method used to set up a sftp connection
        :return: Updates the sftp connection
        """
        self.ssh_connect()
        self.sftp_client: SFTPClient = self.ssh_client.open_sftp()

    def refresh_directory(self, cascade: bool = False):
        """
        Refresh the contents of the directory
        :param cascade: False by default, set to true if you want to refresh even the subdirectories and files
        of all the items in this directory
        :return: Updated directory items
        """
        if not self.check_ssh_connection():
            self.sftp_connect()
        else:
            self.sftp_client: SFTPClient = self.ssh_client.open_sftp()

        stdin, stdout, stderr = self.ssh_client.exec_command(f"find {self.directory} -print")
        pre_config: List[str] = stdout.read().decode().split("\n")
        pre_config.pop(-1)
        pre_config.pop(0)

        for item in pre_config:
            checker = self.sftp_client.lstat(item)
            if S_ISDIR(checker.st_mode):
                self.directory_items.append({"name": Path(item).name,
                                             "object": RemoteDirectory(directory=Path(item),
                                                                       ssh_key=self.__ssh_key,
                                                                       ssh_pass=self.__ssh_password,
                                                                       server_port=self.__ssh_port,
                                                                       server=self.__ssh_server,
                                                                       username=self.__ssh_username,
                                                                       auto_trust=self.__auto_trust,
                                                                       cascade=cascade,
                                                                       active_ssh=self.ssh_client,
                                                                       logger=self.logger),
                                             "type": "directory"})
            else:
                self.directory_items.append({"name": Path(item).name,
                                             "object": RemoteFile(file=Path(item),
                                                                  ssh_key=self.__ssh_key,
                                                                  ssh_pass=self.__ssh_password,
                                                                  server_port=self.__ssh_port,
                                                                  server=self.__ssh_server,
                                                                  username=self.__ssh_username,
                                                                  auto_trust=self.__auto_trust,
                                                                  active_ssh=self.ssh_client,
                                                                  logger=self.logger),
                                             "type": "file"})

    def md5_hash(self) -> str:
        """
        Method used to grab the md5sum of the remote file, used only with compare_md5
        :return: md5 value of file
        """
        if not self.check_ssh_connection():
            self.ssh_connect()
        stdin, stdout, stderr = self.ssh_client.exec_command(f"md5sum {self.__str__()}")
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
            self.sftp_client = self.ssh_client.open_sftp()
        modified_time = ctime(self.sftp_client.file(self.__str__()).stat().st_mtime)
        self.sftp_client.close()
        self.ssh_client.close()
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
        if not self.check_ssh_connection():
            self.sftp_connect()
        else:
            self.sftp_client: SFTPClient = self.ssh_client.open_sftp()
        try:
            self.sftp_client.mkdir(path=self.__str__(), mode=0o755)
            self.sftp_client.close()
            self.ssh_client.close()
            return True
        except PermissionError:
            if self.logger:
                self.logger.warning("You do not have access to this area, please try again")
            self.sftp_client.close()
            self.ssh_client.close()
            return False
        except OSError:
            if self.logger:
                self.logger.warning("The directory already exists, this is not needed")
            self.sftp_client.close()
            self.ssh_client.close()
            return False

    def destination_walker(self, destination: LocalDirectory, reverse: bool = False) -> List[Dict[str, Any]]:
        """
        Walk through a directory and replace the remote root with destination root
        :param destination: LocalDirectory of where the files are going to
        :param reverse: False by default, reverse walk to make remote files
        :return: List of dicts
        """
        if not self.check_ssh_connection():
            self.ssh_connect()
        destination_items: List[Dict[str, LocalFile or LocalDirectory or RemoteFile or RemoteDirectory]] = list()
        if not reverse:
            for item in self.directory_items:
                non_rooted: str = rf"{item['object']}".replace(self.__str__(), "")[1:]
                if item["type"] == "directory":
                    destination_items.append({"name": item["name"],
                                              "object": LocalDirectory(destination.directory.joinpath(non_rooted),
                                                                       logger=self.logger),
                                              "type": "directory"})
                elif item["type"] == "file":
                    destination_items.append({"name": item["name"],
                                              "object": LocalFile(destination.directory.joinpath(non_rooted),
                                                                  logger=self.logger),
                                              "type": "file"})
        else:
            for item in destination.directory_items:
                non_rooted: str = rf"{item['object']}".replace(destination.__str__(), "")[1:]
                if item["type"] == "directory":
                    destination_items.append({"name": item["name"],
                                              "object":
                                                  RemoteDirectory(directory=destination.directory.joinpath(non_rooted),
                                                                  server=self.__ssh_server,
                                                                  username=self.__ssh_username,
                                                                  server_port=self.__ssh_port,
                                                                  ssh_pass=self.__ssh_password,
                                                                  ssh_key=self.__ssh_key,
                                                                  auto_trust=self.__auto_trust,
                                                                  cascade=False,
                                                                  active_ssh=self.ssh_client,
                                                                  logger=self.logger),
                                              "type": "directory"})
                elif item["type"] == "file":
                    destination_items.append({"name": item["name"],
                                              "object": RemoteFile(file=destination.directory.joinpath(non_rooted),
                                                                   server=self.__ssh_server,
                                                                   username=self.__ssh_username,
                                                                   server_port=self.__ssh_port,
                                                                   ssh_pass=self.__ssh_password,
                                                                   ssh_key=self.__ssh_key,
                                                                   auto_trust=self.__auto_trust,
                                                                   active_ssh=self.ssh_client,
                                                                   logger=self.logger),
                                              "type": "file"})
        return destination_items

    def individual_walker(self, source: LocalFile or LocalDirectory) -> dict:
        """
        Walk an individual file or folder from a local directory to make a new remote folder or file for copying
        :param source: Local file or directory
        :return: Dict of information
        """
        if type(source) == LocalFile:
            non_root: str = rf"{source.file.name}"
            return {"name": rf"{non_root}",
                    "object": RemoteFile(file=Path(self.directory.joinpath(non_root)),
                                         server=self.__ssh_server,
                                         username=self.__ssh_username,
                                         server_port=self.__ssh_port,
                                         ssh_pass=self.__ssh_password,
                                         ssh_key=self.__ssh_key,
                                         auto_trust=self.__auto_trust,
                                         logger=self.logger),
                    "type": "file"}
        elif type(source) == LocalDirectory:
            non_root: str = rf"{source.directory.name}"
            return {"name": rf"{non_root}",
                    "object": RemoteDirectory(directory=Path(self.directory.joinpath(non_root)),
                                              server=self.__ssh_server,
                                              username=self.__ssh_username,
                                              server_port=self.__ssh_port,
                                              ssh_pass=self.__ssh_password,
                                              ssh_key=self.__ssh_key,
                                              auto_trust=self.__auto_trust,
                                              logger=self.logger),
                    "type": "folder"}

    def fetch_file(self, remote_file: RemoteFile, copy: bool = False) -> Dict[str, RemoteFile]:
        """
        Fetch file
        :param remote_file: Remote file you're confirming is in this folder and the correct file
        :param copy: Boolean, set to True if you plan to copy the file after as to not close the ssh connection
        False by default
        :return: Confirmed file
        """
        if not self.check_ssh_connection():
            self.sftp_connect()
        else:
            self.sftp_client: SFTPClient = self.ssh_client.open_sftp()
        for file in self.directory_items:
            if file["name"] == remote_file.file.name and file["object"].compare_md5(remote_file.md5_hash(copy=copy)):
                return file
            else:
                pass

    def remote_to_local(self, destination: LocalDirectory) -> True or False:
        """
        Copy the remote directories contents to local folder
        :param destination:
        :return: True or False
        """
        if not self.check_ssh_connection():
            self.sftp_connect()
        else:
            self.sftp_client: SFTPClient = self.ssh_client.open_sftp()
        destination_items: List[LocalFile or LocalDirectory] = self.destination_walker(destination=destination)
        failed_files: List[Dict[str, Exception]] = list()
        if destination.directory.exists():
            pass
        else:
            destination.make_dir()

        for sor, des in zip(self.directory_items, destination_items):
            if des["type"] == "directory":
                if des["object"].directory.exists():
                    pass
                else:
                    des["object"].make_dir()
            elif des["type"] == "file":
                transaction: True or Exception = sor["object"].remote_to_local_copy(des["object"].__str__())
                if isinstance(transaction, Exception):
                    if transaction == FileExistsError:
                        pass
                    else:
                        failed_files.append({"path": des["object"].__str__(), "error": transaction})
                elif transaction:
                    pass

        if len(failed_files) == 0:
            if self.logger:
                self.logger.info("Copy successful")
            return True
        elif len(failed_files) == len(self.directory_items):
            if self.logger:
                self.logger.critical("Full copy unsuccessful")
            return False
        elif 0 < len(failed_files) < len(self.directory_items):
            if self.logger:
                self.logger.warning("Not all files copied completely, check logs for details")
            return False

    def local_to_remote(self, source: LocalDirectory) -> True or False:
        """
        Copy a local directory to remote directory of your choosing
        :param source: Local directory to copy to remote
        :return:Successful copy or failure
        """
        if not self.check_ssh_connection():
            self.sftp_connect()
        else:
            self.sftp_client: SFTPClient = self.ssh_client.open_sftp()
        destination_items: List[Dict[str, RemoteDirectory or RemoteFile]] = self.destination_walker(destination=source,
                                                                                                    reverse=True)
        failed_files: List[Dict[str, Exception]] = list()
        if self.directory_exists():
            pass
        else:
            self.make_dir()

        for sor, des in zip(source.directory_items, destination_items):
            if des["type"] == "directory":
                if des["object"].directory_exists():
                    pass
                else:
                    des["object"].make_dir()
            elif des["type"] == "file":
                transaction: True or Exception = des["object"].local_to_remote_copy(sor["object"].__str__())
                if isinstance(transaction, Exception):
                    if transaction == FileExistsError:
                        pass
                    else:
                        failed_files.append({"path": des["object"].__str__(), "error": transaction})
                elif transaction:
                    pass

        if len(failed_files) == 0:
            if self.logger:
                self.logger.info("Copy successful")
            return True
        elif len(failed_files) == len(source.directory_items):
            if self.logger:
                self.logger.critical("Full copy unsuccessful")
            return False
        elif 0 < len(failed_files) < len(source.directory_items):
            if self.logger:
                self.logger.warning("Not all files copied completely, check logs for details")
            return False

    def recursive_delete(self) -> True or False:
        if not self.check_ssh_connection():
            self.sftp_connect()
        else:
            self.sftp_client: SFTPClient = self.ssh_client.open_sftp()
        directories: List[RemoteDirectory] = [directory["object"] for directory in self.directory_items
                                              if directory["type"] == "directory"]
        directories.reverse()
        files: List[RemoteFile] = [file["object"] for file in self.directory_items if file["type"] == "file"]
        failed_deletions: List[Dict[str, Exception]] = list()
        for file in files:
            delete: True or Exception = file.delete_file()
            if isinstance(delete, Exception):
                if delete == FileNotFoundError:
                    pass
                else:
                    failed_deletions.append({"path": file.__str__(), "error": delete})
            elif delete:
                pass
        if len(failed_deletions) > 0:
            if self.logger:
                self.logger.warning("Could not delete all files, check logs for errors")
            return False
        else:
            for directory in directories:
                delete: True or Exception = directory.rmdir()
                if isinstance(delete, Exception):
                    if delete == FileNotFoundError:
                        pass
                    else:
                        failed_deletions.append({"path": directory.__str__(), "error": delete})
                elif delete:
                    pass
            if len(failed_deletions) > 0:
                if self.logger:
                    self.logger.warning("Although it appears all files were deleted, some folders could not,"
                                        "please investigate this problem")
                return False
            elif len(failed_deletions) == 0:
                if self.logger:
                    self.logger.info("All sub folders and files were deleted")
                return True

    def rmdir(self, force: bool = False) -> True or Exception:
        """
        Delete an entire directory recursively or not, depending on the option
        :param force: False by default, will recursively delete the entire remote directory.
        :return: True or Exception
        """
        if not self.check_ssh_connection():
            self.sftp_connect()
        else:
            self.sftp_client: SFTPClient = self.ssh_client.open_sftp()

        if force:
            try:
                self.recursive_delete()
                self.rmdir()
                return True
            except FileNotFoundError:
                if self.logger:
                    self.logger.info(rf"Directory {self.__str__()} does not exist")
                return FileNotFoundError
            except PermissionError:
                if self.logger:
                    self.logger.warning(rf"You do not have permission to access {self.__str__()} try \
                    again in a new dir")
                return PermissionError
            except OSError:
                if self.logger:
                    self.logger.warning(rf"Directory {self.__str__()} is not empty!")
                return OSError
        else:
            try:
                self.sftp_client.rmdir(self.__str__())
                if self.logger:
                    self.logger.info(rf"Directory {self.__str__()} is deleted")
                return True
            except FileNotFoundError:
                if self.logger:
                    self.logger.info(rf"Directory {self.__str__()} does not exist")
                return FileNotFoundError
            except PermissionError:
                if self.logger:
                    self.logger.warning(rf"You do not have permission to access {self.__str__()} try \
                    again in a new dir")
                return PermissionError
            except OSError:
                if self.logger:
                    self.logger.warning(rf"Directory {self.__str__()} is not empty!")
                return OSError

    def directory_exists(self) -> True or False:
        """
        Method used to check if file exists
        :return: True or False
        """
        if not self.check_ssh_connection():
            self.sftp_connect()
        else:
            self.sftp_client = self.ssh_client.open_sftp()
        try:
            self.sftp_client.stat(self.__str__())
            self.sftp_client.close()
            self.ssh_client.close()
            return True
        except FileNotFoundError:
            if self.logger:
                self.logger.warning(f"Can't find {self.directory}, check that it exists")
            self.sftp_client.close()
            self.ssh_client.close()
            return False

    def remote_to_local_file_copy(self, source: RemoteFile, destination: LocalFile) -> True or Exception:
        """
        Copy one file from the directory to a local destination
        :param source: Remote file entry
        :param destination: Local file entry
        :return: Result of copying file
        """
        file: Dict[str, RemoteFile] = self.fetch_file(source)
        return file["object"].remote_to_local_copy(destination)

    def local_to_remote_file_copy(self, source: LocalFile) -> True or Exception:
        """
        Copy a local file to remote source
        :param source: Local file being copied
        :return: True or Exception
        """
        destination: Dict[str, RemoteFile] = self.individual_walker(source)
        return destination["object"].local_to_remote_copy(source)
