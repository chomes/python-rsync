# python-rsync
Python rsync is a tool to back up files locally and remotely from your computer.
<br>
<br>
I made this as a tool to help develope my python skills but it's a perfectly working script that will do what you need.


<p><b> Versions </b></p>
<p>
<li> Version 1.1 - Config for script enabled for automation of backups between destinations.
</p>

<br>
<br>
<b> What works </b>
<p> <li> Copying files locally from one folder to another folder/internal hd
<li> Copying from local to another host
<li> Copying from a host to a local server </p>
<br>
<br>
<b> What doesn't work </b>
<p> <li> exclude directories
<li> automated rsync backups via config file
<li> Arguments </p>
<br>
<br>
<b> Versions Released </b>
<br>
<li> Version 1.0 - Basic functions of local to local, local to remote server & remote to local backup
<br>
<br>
<b> Future versions in progress </b>
<br>
<br>
<li> Version 1.2 - Provide some type of locking system to stop new backups from running in it's place.
<li> Version 1.3 - Email notifications of when backups are done that include log file
<li> Version 1.3a - Some type of notification letting people know the backup is still on-going
 so it doesn't require checking regularly.

<h3> Instructions </h3>
<p> For the first time run, if you haven't installed rsync before the programme can do this for you, however you need to run it as sudo for the first run for it to do this. It will check your system if rsync exists, if it doesn't it will then install it.
This installation via package repo is supportive of apt and yum</p>

<p> In both manual and automatic the backup assumes you have already loaded your ssh keys on the server or you're using the .config file in ssh to add keys using the IdentityFile line, 
google has plenty of examples :). </p>
<br>
<b> Automated Version: </b>
<li> Provided in script is a config of the different types of backups that are possible.  Delete the config that's not appropiate for you and fill in the information for the backup.
<li> Once you've saved the config run the programme and the backup will read the config and automatically kick off the backup.
<li> Based on if you opted to have a log or not you will be provided with one.
<br>
Here's a breakdown of the different config files:
<br>
<p>[Manual] = local to local
<li> bkoption = Backup option used to decide if you want logs or not, 1 is logs, 2 is not logs.  You must provide a path for logs if you choose option 1, not neccessary if option 2 is selected.
<li> source = directory you want to backup.
<li> destination = location you want to backup to.
<li> log_location = location of log </p>

<p>[LoRem] = Local to remote backup
<li> bkoption = Backup option used to decide if you want logs or not, 1 is logs, 2 is not logs.  You must provide a path for logs if you choose option 1, not neccessary if option 2 is selected.
<li> source = directory you want to backup.
<li> destination = directory you want to backup to.
<li> log_location = location of log 
<li> username = username to connect to the remote server 
<li> remote_server = server you're backing up to
<li> server_port = ssh port to connect, if it's the standard 22 leave as the default in config otherwise change, leaving it blank will stop the backup from running.</p>

<p>[RemLo] = Local to remote backup
<li> bkoption = Backup option used to decide if you want logs or not, 1 is logs, 2 is not logs.  You must provide a path for logs if you choose option 1, not neccessary if option 2 is selected.
<li> source = directory you want to backup.
<li> destination = directory you want to backup to.
<li> log_location = location of log 
<li> username = username to connect to the remote server 
<li> remote_server = server you're backing up to
<li> server_port = ssh port to connect, if it's the standard 22 leave as the default in config otherwise change, leaving it blank will stop the backup from running.</p>
<br>
<br>
<b> Manual Version </b>
<p> If no config file is present when running the programme then software will result to a manual version of the programme asking you to choose what type of backup you want to do.
You can choose between local or remote.  Local is only from one directory to another and remote will let you choose between local to remote or remote to local. </p>
<p> Each one will provide step by step instructions asking you to confirm each section before going to the next incase you make mistakes and will then run the programme.
It will also generate a config file with your options before running in the folder where the file is so you can backup automatically in the future.</p>


