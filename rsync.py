#!/usr/bin/env python3
#Version 0.1
#Version 0.1 basic rsync, next version will include exclude files and to save config into files that script can read from.
#importing functions
from rsync_backups import syncfuncs
import time
#Welcome message
print("Welcome to the Backup script, this will allow you to choose whether you want to back up locally or remotely")
print("You can choose to either back up from remote to local or local to remote it's entirely your choice")
#remote or local backup options
remlo = input("Is this a back up locally from one place to another or a remote server backup? (local OR remote)")
if remlo == 'local':
	lsync = remlo
	print("You have chosen to back up to the {} server/computer lets get started!".format(remlo))
elif remlo == 'remote':
	resync = input("Are you copying from local to remote server or remote server to local? (local OR remote)")
elif resync == 'remote':
	rrsync = resync
	print("You have chosen to do a {} backup to a {} server/computer lets get started!".format(remlo, resync))
elif resync == 'local':
	lrsync = resync
	print("You have chosen to do a {} backup to the {} server/computer lets get started!".format(remlo, resync))
if lsync:
	syncfuncs.localsyn()
elif lrsync:
	syncfuncs.localrem()
elif rrsync:
	syncfuncs.remlocal()
	

	
	
	

	
	