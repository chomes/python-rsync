# blame chomes@
from pathlib import Path
from shutil import copy2
from time import ctime
from typing import Union
from os.path import getmtime
from hashlib import md5
from python_rsync.modules.logger import Logger


class LocalFile:
    def __init__(self, file: Path, logger: Logger or None = None):
        """
        Module used to manipulate local files within your system for copying, and checking md5 sums
        :param file:
        """
        self.file: Union[str, Path] = file
        if logger:
            self.logger: Logger = logger
        else:
            self.logger = None

    def __str__(self) -> str:
        """
        STR method for the file
        :return: str
        """
        return rf"{self.file}"

    def __repr__(self) -> str:
        """
        Repr for working with the module
        :return: str of the file
        """
        return f" Local file: {str(self.file)}"

    def md5_hash(self) -> str:
        """
        Method used to return the md5 sum of the file
        :return: md5sum figure
        """
        return md5(self.file.read_bytes()).hexdigest()

    def compare_md5(self, md5sum: str) -> True or False:
        """
        Method used to check an external md5 value against your own to see if it's the same
        :param md5sum: Other files md5
        :return: True or False
        """
        if self.md5_hash() == md5sum:
            if self.logger:
                self.logger.info("Both file are the same")
            return True
        else:
            if self.logger:
                self.logger.info("Both files are different")
            return False

    def modified_time(self) -> ctime:
        """
        Method used to get modified time on data file
        :return:
        """
        return ctime(getmtime(str(self.file)))

    def transfer_method(self, destination: "LocalFile") -> True or Exception:
        """
        Method used to copy a file over to the destination, it catches all expected errors and returns the
        exception if it doesn't succeed.
        :param destination: Destination of the local file.
        :return:
        """
        try:
            copy2(self.file, destination.file)
            return True
        except PermissionError as e:
            if self.logger:
                self.logger.warning(f"You don't have permission to "
                                    f"{self.__str__()}, please try with the right permissions")
            return e
        except FileNotFoundError as e:
            if self.logger:
                self.logger.warning(f" {self.__str__()} file no longer exists or never did, please try again")
            return e
        except IsADirectoryError as e:
            if self.logger:
                self.logger.warning(f" {self.__str__()} is a directory and not a file, please try again")
            return e

    def copy_file(self, destination: "LocalFile") -> True or Exception:
        """
        The method used to copy the file in it's entirety, it checks if the file exists first,
        if it does it then compares it to the destination and sees if they are the same.
        If the file doesn't exist or it's not the same md5sum, it will copy the file.
        :param destination: Destination path of the file
        :return: Returns either a True or an Exception
        """
        if self.file.exists():
            if not self.compare_md5(destination.md5_hash()):
                if self.logger:
                    self.logger.info(f"File: {destination.__str__()} has been copied")
                return self.transfer_method(destination)
            else:
                if self.logger:
                    self.logger.info(f"File: {destination.__str__()} already exists")
                return FileExistsError
        else:
            return self.transfer_method(destination)

    def delete_file(self) -> True or Exception:
        if self.file.exists():
            self.file.unlink()
            if self.logger:
                self.logger.info(f"File: {self.__str__()} has been deleted")
            return True
        else:
            if self.logger:
                self.logger.info(f"File: {self.__str__()} does not exist")
            return FileNotFoundError
