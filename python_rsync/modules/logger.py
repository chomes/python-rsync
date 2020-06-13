import logging
from pathlib import Path
from typing import Union


class Logger:
    def __init__(self, log_level: str, log_path: Union[str, Path] or None = None):
        self.__leveling: dict = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING,
                                 "critical": logging.CRITICAL}
        self.__log_format: str = "%(asctime)s %(levelname)s %(message)s"
        self.log_path: Union[str, Path] or None = log_path
        if self.log_path:
            logging.basicConfig(format=self.__log_format, level=self.__leveling[log_level.lower()],
                                filename=log_path, filemode="a", datefmt="%d/%m/%Y %H:%M:%S")
        else:
            logging.basicConfig(format=self.__log_format, level=self.__leveling[log_level.lower()],
                                datefmt="%d/%m/%Y %H:%M:%S")
        self.logger: logging = logging
        self.logger.getLogger("paramiko").setLevel(self.logger.WARNING)

    def warning(self, message: str):
        """
        Print warning messages for logging
        :param message: Message you want to print in the log
        :return: Message printed into the log file
        """
        self.logger.warning(message)

    def critical(self, message: str):
        """
        Printing critical messages for logging
        :param message: Message to print into log file
        :return:  Message printed into the log file
        """
        self.logger.critical(message)

    def info(self, message: str):
        """
        Printing info messages for logging
        :param message: Message to print into log file
        :return: Message printed into the log file
        """
        self.logger.info(message)

    def debug(self, message: str):
        """
        Printing debug messages for logging
        :param message: Message printed into the log file
        :return: Message printed
        """
        self.logger.debug(message)
