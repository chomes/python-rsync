# local copy entire folder
# local copy individual files
from typing import Union, Dict, List
from mods.local_file import LocalFile
from pathlib import Path
from hashlib import md5
from os.path import getmtime
from time import ctime
from shutil import copytree


class LocalDirectory:
    def __init__(self, location: Path):
        self.directory: Union[str, Path] = location
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
        self.directory_items: List[Dict[str: str, str: LocalFile or LocalDirectory, str:str]] = list(
            {"name": item.name, "object": LocalFile(item) if item.is_file() else LocalDirectory(item),
             "type": "file" if item.is_file() else "directory"} for item in self.directory.rglob("*"))

    def __repr__(self) -> str:
        return f"Directory {self.directory.stem} has {len(self.directory_items)} files and directories"

    def __str__(self) -> str:
        return f"{str(self.directory)}"

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

    def local_copy_dir(self, local_directory: Union[str, Path]) -> True or Exception:
        """
        Copy the entire tree recursively to a local destination
        :return: Copied action
        """
        if not local_directory.exists():
            try:
                copytree(src=self.directory, dst=local_directory)
                return True
            except PermissionError as e:
                print(f"You don't have permission to {self.__str__()}, please try with the right permissions")
                return e
            except FileNotFoundError as e:
                print(f" {self.__str__()} file no longer exists or never did, please try again")
                return e
            except NotADirectoryError as e:
                print(f" {self.__str__()} is a file and not a directory, please try again")
                return e
        else:
            print("Directory already exists, select a new location")
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
            print(f"{self.__str__()} already exists, not creating directory")
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
                print("This is not a file, it's a directory")
                return IsADirectoryError

