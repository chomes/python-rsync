#!/usr/bin/env python3
# Author: chomes@github
# Current version: 1.5

from configparser import ConfigParser
from pathlib import Path
from python_rsync.modules.sync import RsyncClient
import argparse


def main():
    # User will be forced to use forward slash at all times, validations will be in place to make sure the correct
    # syntax is being used before even attempting to sync to ensure a smooth sync
    # user must use backup to sync specify a source and destination and the programme will handle the work for the user
    # split will be used multiple times to get the data we need to determine:
    # * source and destination, * what type of backup it is (local, lorem, remlo), * username and server for remote

    parser: argparse = argparse.ArgumentParser(description="Sync files locally and remotely")
    parser.add_argument("--config", nargs="?", help="Provide a config file which holds all values you need to backup")
    parser.add_argument("--backup", nargs="?", const=True, help="""Please provide the source and destination, IMPORTANT
    even in a windows machine please use / to specify location i.e. 
    Linux & Mac /home/user/Downloads james@remote-server:/home/backup/dest
    Windows C:/Users/user/Downloads john@backupserver:C:/User/backup/dest
    You can do 3 different ways of syncing:
    1) Local sync: /home/user/backup /home/newuser/destination
    2) remote to local: james@remote-server:/home/user/backup /home/newuser/destination
    3) local to remote: /home/user/Downloads james@remote-server:/home/backup/dest""")
    parser.add_argument("--mirror", nargs="?", const=True,
                        help="Choose this if you want want to mirror sync your backup")
    parser.add_argument("--password", nargs="?", const=True, help="Specify a password for the ssh key")
    parser.add_argument("--sshkey", nargs="?", const=True,
                        help="Specify a location for your ssh key, required for sync password auth is not supported")
    parser.add_argument("--port", nargs="?", const=True, help="Specify the server port, if 22 leave blank")
    parser.add_argument("--loglevel", nargs="?", const=True,
                        help="Info is the default log level specify otherwise for others")
    parser.add_argument("--logpath", nargs="?", const=True,
                        help="If you want to save to a local file specify a path for a log "
                             "to be saved to on your local machine")
    parser.add_argument("--autotrust", nargs="?", const=True,
                        help="Use this if you haven't connected to the server before we'll "
                             "auto accept a trusted connection to make the backup happen")
    parser.add_argument("--emailconfig", nargs="?", const=True, help="If you want emails specify the template")
    args = parser.parse_args()
    if args.config:
        rsync = RsyncClient(sync_config=rf"{args.config}")
