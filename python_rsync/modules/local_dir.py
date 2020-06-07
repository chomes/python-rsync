from typing import Union, Dict, List
from python_rsync.modules.local_file import LocalFile
from pathlib import Path
from hashlib import md5
from os.path import getmtime
from time import ctime
from shutil import copytree, rmtree
from python_rsync.modules.logger import Logger


class LocalDirectory:
    def __init__(self, location: Path, logger: Logger or None):
        """
        Local directory module used to manipulate local files and directories in your physical system
        :param location: Location of the parent directory for the folder you want to manipulate
        """
        self.directory: Union[Path, str] = location
        if self.directory.is_dir():
            pass
        elif self.directory.is_file():
            print("Not a directory")
            raise NotADirectoryError
        elif not self.directory.exists():
            pass
        else:
            print("Something is not right here, either make this non existent directory or an existing dir")
            raise TypeError
        if logger:
            self.logger: Logger = logger
        else:
            self.logger: None = None
        self.directory_items: List[Dict[str, LocalFile or LocalDirectory]] = list(
            {"name": item.name,
             "object": LocalFile(file=item,
                                 logger=self.logger) if item.is_file() else LocalDirectory(location=item,
                                                                                           logger=self.logger),
             "type": "file" if item.is_file() else "directory"} for item in self.directory.rglob("*"))

    def __repr__(self) -> str:
        return f"Directory {self.directory.stem} has {len(self.directory_items)} files and directories"

    def __str__(self) -> str:
        return rf"{self.directory}"

    def md5_hash(self) -> str:
        """
        Get the md5 hash of your directory
        :return: str of your md5sum for the directory
        """
        return md5(self.directory.read_bytes()).hexdigest()

    def compare_md5(self, md5sum) -> True or False:
        """
        Compares the md5sum of the current directory with another to validate if they are the same
        :param md5sum: str value of the md5 of another directory
        :return: True or False
        """
        if self.md5_hash() == md5sum:
            return True
        else:
            return False

    def modified_time(self) -> ctime:
        """
        Get the modified time for this directory
        :return: value of the date for this folder.
        """
        return ctime(getmtime(str(self.directory)))

    def local_copy_dir(self, destination: Union[str, Path]) -> True or Exception:
        """
        Copy the entire tree recursively to a local destination
        :return: Copied action
        """
        if not destination.exists():
            try:
                copytree(src=self.directory, dst=destination)
                return True
            except PermissionError as e:
                if self.logger:
                    self.logger.warning(f"You don't have permission to {self.__str__()}, "
                                        f"please try with the right permissions")
                return e
            except FileNotFoundError as e:
                if self.logger:
                    self.logger.warning(f" {self.__str__()} file no longer exists or never did, please try again")
                return e
            except NotADirectoryError as e:
                if self.logger:
                    self.logger.warning(f" {self.__str__()} is a file and not a directory, please try again")
                return e
        else:
            if self.logger:
                self.logger.warning("Directory already exists, select a new location")
            return IsADirectoryError

    def destination_walker(self, destination: "LocalDirectory") -> List[LocalFile or "LocalDirectory"]:
        """
        Walk through source directory and make a replica of the files and directories to the destionation
        :param destination: Destination directory where you will merge the files and folders to
        :return: List of files and folders to be created and moved
        """
        destination_items: List[LocalFile or LocalDirectory] = list()
        for item in self.directory_items:
            non_rooted: str = rf"{item['object']}".replace(self.__str__(), "")[1:]
            if item["type"] == "directory":
                destination_items.append(LocalDirectory(location=destination.directory.joinpath(non_rooted),
                                                        logger=self.logger))
            elif item["type"] == "file":
                destination_items.append(LocalFile(file=destination.directory.joinpath(non_rooted),
                                                   logger=self.logger))
        return destination_items

    def individual_walker(self, source: LocalFile or "LocalDirectory") -> LocalFile or "LocalDirectory":
        """
        Convert an individual file or folder to the destination path to be copied or created
        :param source: Local file or folder
        :return: The object in the new path
        """
        if type(source) == LocalDirectory:
            non_rooted: str = rf"{source.directory.name}"
            return {"name": rf"{non_rooted}", "object": LocalDirectory(location=self.directory.joinpath(non_rooted),
                                                                       logger=self.logger), "type": "directory"}
        elif type(source) == LocalFile:
            non_rooted: str = rf"{source.file.name}"
            return {"name": rf"{non_rooted}", "object": LocalFile(file=self.directory.joinpath(non_rooted),
                                                                  logger=self.logger), "type": "file"}

    def local_sync_dir(self, destination: "LocalDirectory") -> True or False:
        destination_items = self.destination_walker(destination)
        failed_files: List[Dict[str, Exception]] = list()
        for source, destination in zip(self.directory_items, destination_items):
            if destination["type"] == "directory":
                if not destination["object"].exists():
                    destination["object"].make_dir()
                else:
                    pass
            elif destination["type"] == "file":
                transaction: True or Exception = source["object"].copy_file(destination["object"])
                if isinstance(transaction, Exception):
                    if transaction == FileExistsError:
                        pass
                    else:
                        failed_files.append({"path": destination["object"].__str__(), "error": transaction})
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

    def local_copy_file(self, copy_file: LocalFile, destination: Union[str, Path]) -> True or Exception:
        """
        Copy a file from this directory to another location
        :param copy_file: Name of the file
        :param destination: Destination of the file
        :return: True or exception
        """
        for file in self.directory_items:
            if file["name"] == copy_file.file.name and file["object"].compare_md5(copy_file.md5_hash):
                return file["object"].local_copy(destination)
            else:
                if self.logger:
                    self.logger.info(f" {file['name']} is a directory not a file")
                return IsADirectoryError

    def make_dir(self) -> True or False:
        """
        Make directory when it doesn't exist
        :return: Directory created
        """
        try:
            self.directory.mkdir(mode=0o755)
            return True
        except FileExistsError:
            if self.logger:
                self.logger.warning(f"{self.__str__()} already exists, not creating directory")
            return False

    def rmdir(self, force: bool = False) -> True or False:
        """
        Remove a directory
        :param force: Set to false by default, force a delete even if files and folders exist
        :return: Successful action or not
        """
        if force:
            try:
                rmtree(self.directory)
                if self.logger:
                    self.logger.info(rf"{self.__str__()} has been deleted")
                return True
            except FileNotFoundError:
                if self.logger:
                    self.logger.warning(rf"{self.__str__()} does not exist, not deleting")
                return False
            except PermissionError:
                if self.logger:
                    self.logger.warning(rf"You do not have permission to delete {self.__str__()}, not deleting")
                return False
        else:
            try:
                self.directory.rmdir()
                if self.logger:
                    self.logger.info(rf"{self.__str__()} has been deleted")
                return True
            except FileNotFoundError:
                if self.logger:
                    self.logger.warning(rf"{self.__str__()} does not exist, not deleting")
                return False
            except PermissionError:
                if self.logger:
                    self.logger.warning(rf"You do not have permission to delete {self.__str__()}, not deleting")
                return False

    def directory_exists(self) -> True or False:
        """
        Check if directory exists
        :return: True or False
        """
        if self.directory.exists():
            return True
        else:
            return False
