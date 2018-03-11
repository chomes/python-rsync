#!/usr/bin/env python3
# Version 1.0
# Author: chomes@github
# importing functions
import syncfuncs
from shutil import which


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



# Welcome message
print("Welcome to the Backup script, this will allow you to choose whether you want to back up locally or remotely")
print("\n")
print("You can choose to either back up from remote to local or local to remote it's entirely your choice")
print("\n")
# remote or local backup options
remlo = input("Is this a back up local backup or are you backing up to a remote server? (local OR remote) ").lower()
if remlo == 'local':
    syncfuncs.localsyn()
elif remlo == 'remote':
    resync = input("Is the copy from local or is it from a remote server? (local OR remote) ").lower()
    if resync == 'remote':
        syncfuncs.remlocal()
    elif resync == 'local':
        syncfuncs.localrem()