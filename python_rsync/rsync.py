#!/usr/bin/env python3
# Author: chomes@github
# Current version: 1.5

from shutil import which
from pathlib import Path
from python_rsync.modules.sync import RsyncClient
import argparse


def main():
    parser: argparse = argparse.ArgumentParser()
    parser.add_argument("--source", help="Provide a source path for the directory you're copying from")
    parser.add_argument("--destination", help="Provide a destination path for the directory you're copying to")
    parser.add_argument("--backup", const=True, help="""Choice what type of back: local, remlo, lorem
    local = Local backup only, remlo = Remote to Local backup, lorem = Local to Remote backup""")
    parser.add_argument("--mirror", const=True, help="Choose this if you want want to mirror sync your backup")
    parser.add_argument("--username", const=True, help="Specify a username for the remote server if no config")
    parser.add_argument("--password", const=True, help="Specify a password for the ssh key")
    parser.add_argument("--sshkey", const=True, help="Specify a location for your ssh key, required for sync"
                                                     "password auth is not supported")
    parser.add_argument("--serverport", const=True, help="Specify the server port, if 22 leave blank")
    parser.add_argument("--server", const=True, help="Specify the remote server")
    parser.add_argument("--loglevel", const=True, help="Info is the default log level specify otherwise for others")
    parser.add_argument("--logpath", const=True, help="If you want to save to a local file specify a path for a log"
                                                      "to be saved to on your local machine")
    parser.add_argument("--autotrust", const=True, help="Use this if you haven't connected to the server before"
                                                        "we'll auto accept a trusted connection to make the backup"
                                                        "happen")
    parser.add_argument("--emailconfig", const=True, help="If you want emails specify the template")




