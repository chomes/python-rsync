#!/usr/bin/env python3
# Author: chomes@github
# Current version: 1.3
# Version 1.0 basic rsync with copying locally and remotely.
# Version 1.1 config addition and automation of script.
# Version 1.2 lock file to stop same backup running, along with a way of telling if the backup is still running.
# Version 1.3 email notification
# Future versions:
# Version 1.4 arg parse arguments to allow crons to check periodically if the script is still running
# Version 1.5 Revamp of script to make configs based on clients using arg parse
# Learning: Try and use dictionaries in script if possible for learning.

# Importing functions
from mods import syncfuncs
from shutil import which
from pathlib import Path
import configparser

# Checking if user has rsync installed
if which("rsync") is not None:
    print("")
else:
    print("Rsync is not installed, installing please make sure you run the app in sudo or this won't work")
    if which("apt") is not None:
        syncfuncs.install_apt("rsync")
        print("Package has been installed, exiting app, please run without sudo")
        exit()
    elif which("yum") is not None:
        syncfuncs.install_yum("rsync")
        print("Package has been installed, exiting app, please run without sudo")
        exit()


# If statement to determine manual or automated backup
config_file = Path("config.ini")
if config_file.is_file():
    config = configparser.ConfigParser()
    config.read("config.ini")
    if 'Manual' in config:
        syncfuncs.lsyauto()
    elif 'LoRem' in config:
        syncfuncs.loreauto()
    elif 'RemLo' in config:
        syncfuncs.reloauto()
else:
    print("Config not found, manual backup is starting")
    # Welcome message
    print("Welcome to the Backup script, this will allow you to choose whether you want to back up locally or remotely")
    print("You can choose to either back up from remote to local or local to remote it's entirely your choice")

    # remote or local backup options
    remlo = input("Is this a back up locally from one place to another or a remote server backup? (local OR remote)")
    if remlo == 'local':
        syncfuncs.localsyn()
    elif remlo == 'remote':
        resync = input("Are you copying from local to remote server or remote server to local? (local OR remote)")
        if resync == 'remote':
            syncfuncs.remlocal()
        elif resync == 'local':
            syncfuncs.localrem()
