#!/usr/bin/env python3
# Author:chomes@github
# Defining functions
# Time used for sleeping
import time
from subprocess import Popen
from pathlib import Path
from configparser import ConfigParser
import getpass
from mods.email import EmailClient


class RsyncClient:
    def __init__(self, file):
        self.sor


# Function for apt install of package
def install_apt(pkg_name):
    """Installing package using apt library, requires arg in function call
    e.g: rsync = "rsync" install_apt(rsync)
    """
    cache = apt.Cache()
    cache.update()
    pkg = cache[pkg_name]
    pkg.mark_install()
    cache.commit()


# Function for yum install of package
def install_yum(pkg_name):
    """Installing package using call method for yum installs, must provide arg in function.
    eg: rsync = "rsync install_yum(rsync)
    """
    rsync_install = ["yum", "install", pkg_name, "-y"]
    call(rsync_install)


# Local sync function
def sync_call_manual(startbk, sor, des, logloc, lock_name):
    """ Function to run rsync inside the server from one folder to another, requires multiple arguments in function to
     run.
    startbk is either 1 or 2 to determine if you want a log or not
    sor is the source of the folder you want to copy
    des is the destination of the folder you want to copy
    logloc is the location of the log file if it exists
    lock_name is the shortened name of the config file for the backup
    """
    lock_path = lock_name + '.lock'
    # if statement if lock exists don't run backup otherwise continue function
    if Path(lock_path).exists():
        print("Back up is already taking place, exiting program, wait till backup is done")
        email_funcs.backup_in_progress()
        exit()
    else:
        if startbk == 1:
            timestamp = time.strftime("%Y%m%d-%H%M")
            logloc = logloc + timestamp
            logloc = logloc + "-logfile"
            print("Starting backup, rsync -avv {} {} --log-file={}".format(sor, des, logloc))
            email_funcs.backup_start()
            lclresyn = ["rsync", "-avv", sor, des, "--log-file", logloc]
            Path(lock_path).touch()
            call(lclresyn)
            time.sleep(1)
            Path(lock_path).unlink()
            print("The backup is now complete! Check the logs at {} for details on what was backed up".format(logloc))
            email_funcs.backup_completed(logloc)
        elif startbk == 2:
            print("Starting backup, rsync -avv {} {} ".format(sor, des))
            email_funcs.backup_start()
            lclresynnl = ["rsync", "-avv", sor, des]
            Path(lock_path).touch()
            call(lclresynnl)
            time.sleep(1)
            Path(lock_path).unlink()
            print("The backup is now complete!")
            email_funcs.backup_completed(log_loc=None)


# Function for remote to local & local to remote
def sync_call_lorem(startbk, sor, des, usn, remserv, servport, logloc, lock_name):
    """Function to run rsync from the local server to a remote one for backup purposes, requires arguments to run.
    It also is the same function from remote to local server depending on what startbk number is
    startbk is 1-4 determining if it's local > remote or remote > local along with if you want logs or not.
    sor is the source of the folder you want to copy
    des is the destination of the folder you want to copy
    usn is the username for the remote server
    remserv is the hostname for the server, must be a name the local server can resolve to for this to work
    logloc is the location of the log file if it exists
    lock_name is the shortened name of the config file for the backup
    """
    lock_path = lock_name + '.lock'
    # if statement if lock exists don't run backup otherwise continue function
    if Path(lock_path).exists():
        print("Back up is already taking place, exiting program, wait till backup is done")
        exit()
    else:
        if startbk == 1:
            timestamp = time.strftime("%Y%m%d-%H%M")
            logloc = logloc + timestamp
            logloc = logloc + "-logfile"
            print('''Starting backup, rsync -avv 'ssh -p {}'
            {} {}@{}:{} --log-file={}'''.format(servport, sor, usn, remserv, des, logloc))
            email_funcs.backup_start()
            ds = '%s@%s:%s' % (usn, remserv, des)
            lcremlg = 'rsync -avv --port=%s %s %s --log-file %s' % (servport, sor, ds, logloc)
            Path(lock_path).touch()
            # shell required to run the command properly
            p1 = subprocess.Popen(lcremlg, shell=True).wait()
            print(p1)
            time.sleep(1)
            Path(lock_path).unlink()
            print("The backup is now complete! Check the logs at {} for details on what was backed up".format(logloc))
            email_funcs.backup_completed(logloc)
        elif startbk == 2:
            print("Starting backup, rsync -avv 'ssh -p {}' {} {}@{}:{}".format(servport, sor, usn, remserv, des))
            email_funcs.backup_start()
            ds = '%s@%s:%s' % (usn, remserv, des)
            lcremnl = 'rsync -avv --port=%s %s %s' % (servport, sor, ds)
            Path(lock_path).touch()
            # shell required to run the command properly
            p1 = subprocess.Popen(lcremnl, shell=True).wait()
            print(p1)
            time.sleep(1)
            Path(lock_path).unlink()
            print("The backup is now complete!")
            email_funcs.backup_completed(log_loc=None)
        elif startbk == 3:
            print(''' Starting backup, rsync -avv 'ssh -p {}' 
            {}@{}:{} {}'''.format(servport, sor, usn, remserv, des))
            email_funcs.backup_start()
            se = '%s@%s:%s' % (usn, remserv, sor)
            remlcnl = 'rsync -avv --port=%s %s %s' % (servport, se, des)
            Path(lock_path).touch()
            # shell required to run the command properly
            p1 = subprocess.Popen(remlcnl, shell=True).wait()
            print(p1)
            time.sleep(1)
            Path(lock_path).unlink()
            print("The backup is now complete!")
            email_funcs.backup_completed(log_loc=None)
        elif startbk == 4:
            timestamp = time.strftime("%Y%m%d-%H%M")
            logloc = logloc + timestamp
            logloc = logloc + "-logfile"
            print('''Starting backup, rsync -avv 'ssh -p {}'
            {}@{}:{} {} --log-file={}'''.format(servport, usn, remserv, sor, des, logloc))
            email_funcs.backup_start()
            se = '%s@%s:%s' % (usn, remserv, sor)
            remlclg = 'rsync -avv --port=%s %s %s > %s' % (servport, se, des, logloc)
            Path(lock_path).touch()
            # shell required to run the command properly
            p1 = subprocess.Popen(remlclg, shell=True).wait()
            print(p1)
            time.sleep(1)
            Path(lock_path).unlink()
            print("The backup is now complete! Check the logs at {} for details on what was backed up".format(logloc))
            email_funcs.backup_completed(logloc)


# Creating manual backup of local copy
def localsyn():
    """This function goes through the process of creating a local backup if you don't have a config file,
     requires no arguments.
     """
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
            startbk = 2
            print("Saving to config for automation later")
            config = configparser.ConfigParser()
            config['Manual'] = {'bkoption': startbk,
                                'source': sor,
                                'destination': des,
                                'log_location': logloc}
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
                configfile.close()
            print("Config file saved. No logs required running backup!")
            lock_name = Path("config.ini").stem
            sync_call_manual(startbk, sor, des, logloc, lock_name)
            break
        elif logging == "y":
            logloc = input("Please type the destination of the log: ")
            if logloc.endswith("/"):
                conf_log = input("Are you happy with the destination {} ? y or n ".format(logloc)).lower()
                if conf_log == "y":
                    startbk = 1
                    print("Saving to config for automation later")
                    config = configparser.ConfigParser()
                    config['Manual'] = {'bkoption': startbk,
                                        'source': sor,
                                        'destination': des,
                                        'log_location': logloc}
                    with open('config.ini', 'w') as configfile:
                        config.write(configfile)
                        configfile.close()
                    print("Config saved. Ok, lets run the backup!")
                    lock_name = Path("config.ini").stem
                    sync_call_manual(startbk, sor, des, logloc, lock_name)
                    break
                else:
                    print("Ok, lets change the destination")
                    continue
            else:
                print("Destination must end with a / please try again")
                continue


# local to remote server backup
def localrem():
    """Function to go through the set up process of creating a backup if config is provided for local to remote server.
    No arg required
    """
    print("Now we will choose the source and destination")
    sor = input("What is the FULL PATH to the directory you want to backup? ")
    des = input("What is the FULL PATH to the directory you want to copy to? ")
    usn = input('''Please state the user for the backup,
    if you don't state one we'll use the default one {} '''.format(getpass.getuser()))
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
            usn = input('''Please state the user for the backup, 
            if you don't state one we'll use the default one {} '''.format(getpass.getuser()))
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
            startbk = 2
            print("Saving to config for automation later")
            config = configparser.ConfigParser()
            config['LoRem'] = {'bkoption': startbk,
                               'source': sor,
                               'destination': des,
                               'log_location': logloc,
                               'username': usn,
                               'remote_server': remserv,
                               'server_port': servport}
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
                configfile.close()
            print("Config saved.  No logs required running backup!")
            lock_name = Path("config.ini").stem
            sync_call_lorem(startbk, sor, des, usn, remserv, servport, logloc, lock_name)
            break
        elif logging == "y":
            logloc = input("Please type the destination of the log: ")
            if logloc.endswith("/"):
                conf_log = input("Are you happy with the destination {} ? y or n ".format(logloc)).lower()
                if conf_log == "y":
                    startbk = 1
                    print("Saving to config for automation later")
                    config = configparser.ConfigParser()
                    config['LoRem'] = {'bkoption': startbk,
                                       'source': sor,
                                       'destination': des,
                                       'log_location': logloc,
                                       'username': usn,
                                       'remote_server': remserv,
                                       'server_port': servport}
                    with open('config.ini', 'w') as configfile:
                        config.write(configfile)
                        configfile.close()
                    print("Config saved.  Ok lets run the backup!")
                    lock_name = Path("config.ini").stem
                    sync_call_lorem(startbk, sor, des, usn, remserv, servport, logloc, lock_name)
                    break
                else:
                    print("Ok, lets change the destination")
                    continue
            else:
                print("Destination must end with a / please try again")
                continue


# remote to local server backup
def remlocal():
    """Function for a step by stepp process of creating a remote to local backup if no config is provided,
    no arg required.
    """
    print("Now we will choose the source and destination")
    sor = input("What is the FULL PATH to the directory you want to copy from? ")
    des = input("What is the FULL PATH to the directory you want to copy to? ")
    usn = input('''Please state the user for the backup,
    if you don't state one we'll use the default one {} '''.format(getpass.getuser()))
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
            usn = input('''Please state the user for the backup,
            if you don't state one we'll use the default one {} '''.format(getpass.getuser()))
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
            startbk = 3
            print("Saving to config for automation later")
            config = configparser.ConfigParser()
            config['RemLo'] = {'bkoption': startbk,
                               'source': sor,
                               'destination': des,
                               'log_location': logloc,
                               'username': usn,
                               'remote_server': remserv,
                               'server_port': servport}
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
                configfile.close()
            print("Config saved.  Ok lets run the backup!")
            lock_name = Path("config.ini").stem
            sync_call_lorem(startbk, sor, des, usn, remserv, servport, logloc, lock_name)
            break
        elif logging == "y":
            logloc = input("Please type the destination of the log: ")
            if logloc.endswith("/"):
                conf_log = input("Are you happy with the destination {} ? y or n ".format(logloc)).lower()
                if conf_log == "y":
                    startbk = 4
                    print("Saving to config for automation later")
                    config = configparser.ConfigParser()
                    config['RemLo'] = {'bkoption': startbk,
                                       'source': sor,
                                       'destination': des,
                                       'log_location': logloc,
                                       'username': usn,
                                       'remote_server': remserv,
                                       'server_port': servport}
                    with open('config.ini', 'w') as configfile:
                        config.write(configfile)
                        configfile.close()
                    print("Config saved.  Ok lets run the backup!")
                    lock_name = Path("config.ini").stem
                    sync_call_lorem(startbk, sor, des, usn, remserv, servport, logloc, lock_name)
                    break
                else:
                    print("Ok, lets change the destination")
                    continue
            else:
                print("Destination must end with a / please try again")
                continue


# Automated backup for local
def lsyauto():
    """Function for running an automated local to local backup, no arg required, reads the config provided"""
    print("Reading config")
    config = configparser.ConfigParser()
    config.read("config.ini")
    if config.get("Manual", "bkoption") == '1':
        startbk = 1
    else:
        startbk = 2
    sor = config.get("Manual", "source")
    des = config.get("Manual", "destination")
    logloc = config.get("Manual", "log_location")
    print("Running backup from {} to {}".format(sor, des))
    lock_name = Path("config.ini").stem
    sync_call_manual(startbk, sor, des, logloc, lock_name)


# Automated backup for local to remote
def loreauto():
    """Function for running an automated local to remote backup, no arg required, reads the config provided"""
    print("Reading config")
    config = configparser.ConfigParser()
    config.read("config.ini")
    if config.get("LoRem", "bkoption") == '1':
        startbk = 1
    else:
        startbk = 2
    sor = config.get("LoRem", "source")
    des = config.get("LoRem", "destination")
    logloc = config.get("LoRem", "log_location")
    usn = config.get("LoRem", "username")
    remserv = config.get("LoRem", "remote_server")
    servport = config.get("LoRem", "server_port")
    print("Running backup")
    lock_name = Path("config.ini").stem
    sync_call_lorem(startbk, sor, des, usn, remserv, servport, logloc, lock_name)


# Automated backup for remote to local
def reloauto():
    """Function for running an automated local to remote backup, no arg required, reads the config provided"""
    print("Reading config")
    config = configparser.ConfigParser()
    config.read("config.ini")
    if config.get("RemLo", "bkoption") == '3':
        startbk = 3
    else:
        startbk = 4
    sor = config.get("RemLo", "source")
    des = config.get("RemLo", "destination")
    logloc = config.get("RemLo", "log_location")
    usn = config.get("RemLo", "username")
    remserv = config.get("RemLo", "remote_server")
    servport = config.get("RemLo", "server_port")
    print("Running backup")
    lock_name = Path("config.ini").stem
    sync_call_lorem(startbk, sor, des, usn, remserv, servport, logloc, lock_name)
