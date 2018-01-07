#!/usr/bin/env python3

# Defining functions
import time
from subprocess import call
import configparser


# Calling function to run
def sync_call_manual(startbk, sor, des, logloc):
    if startbk == 1:
        print("Starting backup, rsync -avv {} {} --log-file={}".format(sor, des, logloc))
        lclresyn = ["rsync", "-avv", sor, des, "--log-file", logloc]
        call(lclresyn)
        time.sleep(1)
        print("The backup is now complete! Check the logs at {} for details on what was backed up".format(logloc))
    elif startbk == 2:
        print("Starting backup, rsync -avv {} {} ".format(sor, des))
        lclresynnl = ["rsync", "-avv", sor, des]
        call(lclresynnl)
        time.sleep(1)
        print("The backup is now complete!")


# Creating manual backup of local copy
def localsyn():
    print("Now we will choose the source and destination")
    sor = input("What is the FULL PATH to the directory you want to backup? ")
    des = input("What is the FULL PATH to the directory you want to copy to? ")
    print("We will copy from {} to {}".format(sor, des))
    # loop statement for changing sor or des
    while True:
        change = input("Did you want to make changes to source or destination? (source, destination, no)")
        if change == 'source':
            sor = input("What is the FULL PATH to the directory you want to backup? ")
            print("We will copy from {} to {}".format(sor, des))
            continue
        elif change == 'destination':
            des = input("What is the FULL PATH to the dorectory you want to copy to? ")
            print("We will copy from {} to {}".format(sor, des))
            continue
        elif change == 'no':
            print("We will now begin the backup!")
            break
    # loop for logging backup
    while True:
        logging = input("Do you want a log of the backup? (y or n)").lower()
        if logging == "n":
            logloc = ""
            print("No logs required running backup!")
            startbk = 2
            sync_call_manual(startbk, sor, des, logloc)
            break
        elif logging == "y":
            logloc = input("Please type the destination of the log: ")
            if logloc.endswith("/"):
                conf_log = input("Are you happy with the destination {} ? y or n ".format(logloc)).lower()
                if conf_log == "y":
                    timestamp = time.strftime("%Y%m%d-%H%M")
                    logloc = logloc + timestamp
                    logloc = logloc + "-logfile"
                    startbk = 1
                    print("Ok lets run the backup!")
                    sync_call_manual(startbk, sor, des, logloc)
                    break
                else:
                    print("Ok, lets change the destination")
                    continue
            else:
                print("Destination must end with a / please try again")
                continue

# local to remote server backup
def localrem():
    print("Now we will choose the source and destination")
    sor = input("What is the FULL PATH to the directory you want to backup? ")
    des = input("What is the FULL PATH to the directory you want to copy to? ")
    print("We will copy from {} to {}".format(sor, des))
    while True:
        change = input("Did you want to make changes to source or destination? (source, destination, no)")
        if change == 'source':
            sor = input("What is the FULL PATH to the directory you want to backup? ")
            print("We will copy from {} to {}".format(sor, des))
            continue
        elif change == 'destination':
            des = input("What is the FULL PATH to the dorectory you want to copy to? ")
            print("We will copy from {} to {}".format(sor, des))
            continue
        elif change == 'no':
            print("We will now begin the backup!")
            break

    logging = input("Do you want a log of the backup? (y or n)")
        elif logging == 'n':
            print("No logging required, we will start the backup!")
            startbk = 2
        elif logging == 'y':
            logloc = input("Please specify the FULL PATH of where you want the log to be saved? ")
            print("The log will be located at {}".format(logloc))
            logch = input("Did you want to change the location? (y or n)")
        elif logch == 'y':
            logloc = input("Please specify the FULL PATH of where you want the log to be saved? ")
            print("The log will be located at {}".format(logloc))
            logch = input("Did you want to change the location? (y or no)")
        elif logch == 'n':
            print("We will now start the backup!")
            startbk = 1