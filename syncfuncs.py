#!/usr/bin/env python3
# Author:chomes@github
# Defining functions
import time
import subprocess
from subprocess import call
import getpass
import apt


# Package for installing apt
def install_apt(pkg_name):
    cache = apt.Cache()
    cache.update()
    pkg = cache[pkg_name]
    pkg.mark_install()


def install_yum(pkg_name):
    rsync_install = ['yum install %s -y' % (pkg_name)]
    call(rsync_install)


# Local sync function
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


# Function for remote to local & local to remote
def sync_call_lorem(startbk, sor, des, usn, remserv, servport, logloc):
    if startbk == 1:
        timestamp = time.strftime("%Y%m%d-%H%M")
        logloc = logloc + timestamp
        logloc = logloc + "-logfile"
        print('''Starting backup, rsync -avv 'ssh -p {}'
        {} {}@{}:{} --log-file={}'''.format(servport, sor, usn, remserv, des, logloc))
        ds = '%s@%s:%s' % (usn, remserv, des)
        lcremlg = 'rsync -avv --port=%s %s %s --log-file %s' % (servport, sor, ds, logloc)
        # shell required to run the command properly
        p1 = subprocess.Popen(lcremlg, shell=True).wait()
        print(p1)
        time.sleep(1)
        print("The backup is now complete! Check the logs at {} for details on what was backed up".format(logloc))
    elif startbk == 2:
        print("Starting backup, rsync -avv 'ssh -p {}' {} {}@{}:{}".format(servport, sor, usn, remserv, des))
        ds = '%s@%s:%s' % (usn, remserv, des)
        lcremnl = 'rsync -avv --port=%s %s %s' % (servport, sor, ds)
        # shell required to run the command properly
        p1 = subprocess.Popen(lcremnl, shell=True).wait()
        print(p1)
        time.sleep(1)
        print("The backup is now complete!")
    elif startbk == 3:
        print(''' Starting backup, rsync -avv 'ssh -p {}' 
        {}@{}:{} {}'''.format(servport, sor, usn, remserv, des))
        se = '%s@%s:%s' % (usn, remserv, sor)
        remlcnl = 'rsync -avv --port=%s %s %s' % (servport, se, des)
        # shell required to run the command properly
        p1 = subprocess.Popen(remlcnl, shell=True).wait()
        print(p1)
        time.sleep(1)
        print("The backup is now complete!")
    elif startbk == 4:
        timestamp = time.strftime("%Y%m%d-%H%M")
        logloc = logloc + timestamp
        logloc = logloc + "-logfile"
        print('''Starting backup, rsync -avv 'ssh -p {}'
        {}@{}:{} {} --log-file={}'''.format(servport, usn, remserv, sor, des, logloc))
        se = '%s@%s:%s' % (usn, remserv, sor)
        remlclg = 'rsync -avv --port=%s %s %s > %s' % (servport, se, des, logloc)
        # shell required to run the command properly
        p1 = subprocess.Popen(remlclg, shell=True).wait()
        print(p1)
        time.sleep(1)
        print("The backup is now complete! Check the logs at {} for details on what was backed up".format(logloc))


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
    # Loop to make sure directory ends with /
    while True:
        sor = input("What is the FULL PATH to the directory you want to backup? ")
        if sor.endswith("/"):
            break
        else:
            print("Directory must have a / at the end, please add one")
    while True:
        des = input("What is the FULL PATH to the directory you want to copy to? ")
        if des.endswith("/"):
            break
        else:
            print("Directory must have a / at the end, please add one")
    usn = input("What's the username? If none given we'll use the current {}".format(getpass.getuser()))
    if not usn:
        usn = getpass.getuser()
    remserv = input("What is the server you want to connect to? ")
    servport = input("What is the server port? If you don't choose one we will default to normal ssh ")
    if not servport:
        servport = 22
    print("We will copy from {} to {}{}{} on port {}".format(sor, usn, remserv, des, servport))
    # Loop for final changes to backup
    while True:
        change = input("Did you want to make any changes? (source, destination, port, username, server, no)").lower()
        if change == 'source':
            sor = input("What is the FULL PATH to the directory you want to backup? ")
            if sor.endswith("/"):
                print("We will copy from {} to {}".format(sor, des))
                continue
            else:
                print("The directory must have a / please add one")
        elif change == 'destination':
            des = input("What is the FULL PATH to the dorectory you want to copy to? ")
            if sor.endswith("/"):
                print("We will copy from {} to {}".format(sor, des))
                continue
            else:
                print("The directory must have a / please add one")
        elif change == 'port':
            servport = input("What is the server port? If you don't choose one we will default to normal ssh ")
            if not servport:
                servport = 22
            print("The port you have chosen is {}".format(servport))
            continue
        elif change == 'username':
            usn = input("What's the username? If none given we'll use the current {}".format(getpass.getuser()))
            print("The username you have chosen is {}".format(usn))
            continue
        elif change == 'server':
            remserv = input("What is the server you want to connect to? ")
            print("The remote server is: {}".format(remserv))
            continue
        elif change == 'no':
            print("We will now begin the backup!")
            break
    # Log file for the backup
    while True:
        logging = input("Do you want a log of the backup? (y or n)").lower()
        if logging == "n":
            logloc = ""
            print("No logs required running backup!")
            startbk = 2
            sync_call_lorem(startbk, sor, des, usn, remserv, servport, logloc)
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
                    sync_call_lorem(startbk, sor, des, usn, remserv, servport, logloc)
                    break
                else:
                    print("Ok, lets change the destination")
                    continue
            else:
                print("Destination must end with a / please try again")
                continue


# remote to local server backup
def remlocal():
    print("Now we will choose the source and destination")
    sor = input("What is the FULL PATH to the directory you want to copy from? ")
    des = input("What is the FULL PATH to the directory you want to copy to? ")
    usn = input("What's the username? If none given we'll use the current {}".format(getpass.getuser()))
    if not usn:
        usn = getpass.getuser()
    remserv = input("What is the server you want to connect to? ")
    servport = input("What is the server port? If you don't choose one we will default to normal ssh ")
    if not servport:
        servport = 22
    print("We will copy from {}@{}:{} on port {} to {}".format(usn, remserv, sor, servport, des))
    # Loop for final changes to backup
    while True:
        change = input("Did you want to make any changes? (source, destination, port, username, server, no)").lower()
        if change == 'source':
            sor = input("What is the FULL PATH to the directory you want to backup? ")
            print("We will copy from {} to {}".format(sor, des))
            continue
        elif change == 'destination':
            des = input("What is the FULL PATH to the dorectory you want to copy to? ")
            print("We will copy from {} to {}".format(sor, des))
            continue
        elif change == 'port':
            servport = input("What is the server port? If you don't choose one we will default to normal ssh ")
            if not servport:
                servport = 22
            print("The port you have chosen is {}".format(servport))
            continue
        elif change == 'username':
            usn = input("What's the username? If none given we'll use the current {}".format(getpass.getuser()))
            print("The username you have chosen is {}".format(usn))
            continue
        elif change == 'server':
            remserv = input("What is the server you want to connect to? ")
            print("The remote server is: {}".format(remserv))
            continue
        elif change == 'no':
            print("We will now begin the backup!")
            break
    # Log file for the backup
    while True:
        logging = input("Do you want a log of the backup? (y or n)").lower()
        if logging == "n":
            logloc = ""
            print("No logs required running backup!")
            startbk = 3
            sync_call_lorem(startbk, sor, des, usn, remserv, servport, logloc)
            break
        elif logging == "y":
            logloc = input("Please type the destination of the log: ")
            if logloc.endswith("/"):
                conf_log = input("Are you happy with the destination {} ? y or n ".format(logloc)).lower()
                if conf_log == "y":
                    timestamp = time.strftime("%Y%m%d-%H%M")
                    logloc = logloc + timestamp
                    logloc = logloc + "-logfile"
                    startbk = 4
                    print("Ok lets run the backup!")
                    sync_call_lorem(startbk, sor, des, usn, remserv, servport, logloc)
                    break
                else:
                    print("Ok, lets change the destination")
                    continue
            else:
                print("Destination must end with a / please try again")
                continue