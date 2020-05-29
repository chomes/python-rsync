# blame chomes@
from pathlib import Path
from shutil import copy2
from time import ctime
from typing import Union
from os.path import getmtime
from hashlib import md5
import logging


class LocalFile:
    def __init__(self, file: Path):
        self.file: Union[str, Path] = file

    def __str__(self) -> str:
        """
        STR method for the file
        :return: str
        """
        return str(self.file)

    def __repr__(self) -> str:
        """
        Repr for working with the module
        :return: str of the file
        """
        return str(self.file)

    def __md5_hash(self) -> str:
        """
        Method used to return the md5 sum of the file
        :return: md5sum figure
        """
        return md5(self.file.read_bytes()).hexdigest()

    def compare_md5(self, file_md5: str) -> True or False:
        """
        Method used to check an external md5 value against your own to see if it's the same
        :param file_md5: Other files md5
        :return: True or False
        """
        if self.__md5_hash() == file_md5:
            return True
        else:
            return False

    def modified_time(self) -> ctime:
        """
        Method used to get modified time on data file
        :return:
        """
        return ctime(getmtime(str(self.file)))

    def local_copy(self, destination: Union[str, Path]):
        try:
            copy2(self.file, destination)
        except PermissionError as e:
            print(f"""You don't have permission to this file, please try with the right permissions
            Error: {e}""")
        except FileNotFoundError as e:
            print(f""" This file no longer exists or never did, please try again
            Error: {e} """)
