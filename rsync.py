#!/usr/bin/env python3
# Author: chomes@github
# Current version: 1.0
# Version 0.1 basic rsync with copying locally and remotely.
# Version 1.0 config addition and automation of script
# Future versions:
# Version 1.1 lock file to stop same backup running, along with a way of telling if the backup is still running.
# Version 1.2 email notification

# importing functions
import syncfuncs
from pathlib import Path
import configparser


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
