#!/bin/bash
#
#
# fairly simple linear script to create a login for use with the ftp system
# which will generate a password, and email it to the specified address.
# also prompts for a WD request number.
#
# TODO: more sanity checking..

if [ $# -lt 3 ]
then
   echo need username helpdesknumber emailaddress [emailaddress] [emailaddress] ...
   echo as commandline arguments.
   exit 1
fi
USER=$1
WDJOB=$2
# this will adjust the command line params so only the 1 or more email addresses are left.
shift
shift
# so we grab all the remaining parameters as they should be whitespace delimited email addresses.
EMAILADDR=$@

# check for valid email addresses with the rest of the line....

regex="^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$"

while [ $# -gt 0 ]
do 
   email=$1
   if [[ "$email" =~ $regex ]]
   then
      echo "Email address $email is valid."
   else
      echo "Email address $email is invalid."
      exit 1
   fi
   shift
done

if [ $USER = "ALL" ]
then
   echo user name cannot be ALL
   exit 1
fi

# existing user check
if id -u $USER &>/dev/null
then
   echo account named $USER already exists
   exit 1
fi


echo creating ftp user with login $USER ftpmanager addresses $EMAILADDR and wonderdesk ref $WDJOB

/usr/sbin/adduser --quiet \
        --shell /bin/rbash \
        --disabled-login \
        --gecos ",,,,"  \
        --home /home/$USER $USER
# the chfn used by adduser above too limited, so we use usermod to update the gegos info
# without hitting dumb limits
usermod $USER -c "WD$WDJOB FTPMANAGER $EMAILADDR"

chmod o-rwx /home/$USER

/usr/admin/util/ftp_change_password.py NEW $USER

