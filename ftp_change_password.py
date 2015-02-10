#!/usr/bin/python
#
#  Script to change the password of a list of ftp accounts, and email
#  the new password to a recipient who has been defined in the comments
#  field of the password file. Intended to be run from CRON so we rotate
#  passwords weekly (or monthly??) for certain ftp accounts.
#
# 4/01/2013 - now can have a whitespace list of email addresses as well as a single
#             email address after FTPMANAGER and it will email to all addresses mentioned.
#

import subprocess, smtplib, pwd, re, sys


#
# message bodies.. different one for first account creation email (NEW cmd line param), and subsequent password update
# email 
#
# params replaced in below message texts are (sender,email,ftpaccount,ftpaccount,newpassword)

# for newly created accounts:
newaccount = """From: Company IT <%s>
To: <%s>
Subject: ftp account %s created for you to use.

An ftp account has been created according to an IT support request, and this is one of the addresses requested to get the credentials.

The password for ftp account %s is %s

The server is ftp.companyname.com.au 

We advise using the 'filezilla' free ftp client if you find you are having ftp problems with other ftp clients such as Internet Explorer.

regards,
System Administrators

"""

# for password update emails:
passwordchange = """From: Company IT <%s>
To: <%s>
Subject: password update for ftp account %s

The new password for ftp account %s is %s

Please forward these new credentials on to any users of the ftp account.

""" 


# commandline params
# if we get "ALL" we process the entire passwd file
# otherwise we do it for the accounts specified

if len(sys.argv) < 2:
   print "Usage:"
   print "  ",sys.argv[0]," ALL"
   print "   to change and email out for all configured ftp accounts"
   print "   or"
   print "  ",sys.argv[0]," <account1> <account2> ..."
   print "   to do for a subset of ftp accounts."
   print "   or"
   print "  ",sys.argv[0]," NEW <account1> <account2> ..."
   print "   to do for a subset of ftp accounts, but sending the initial account creation email text."
   exit(0)

#
# todo: store in config file or database? or fetch info from /etc/passwd even...
#
# if comments field in password has "FTPMANAGER ", string following to end of comment
# is the email address to use
#
sender = 'sysadmin@company.com.au'
emaildelimiter = 'FTPMANAGER '
managedaccounts = {}

def validemails(emaillist):
   for manageremail in emaillist:
      # check validity of emails 
      if not re.match("^[A-Za-z0-9'\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$", manageremail):
         print "regex didnt match ",manageremail, " deemed not a valid email address, not handling this account"
         return False
   return True

for account in pwd.getpwall():
   if len(account.pw_gecos.split(emaildelimiter)) == 2:
      ftpaccount = account.pw_name
      manageremails = account.pw_gecos.split(emaildelimiter)[1]
      manageremail = manageremails.split()
      # should be a list of emails, but we check..
      # print manageremail
     
      # check validity of emails with regex
      if validemails(manageremail):
         managedaccounts[ftpaccount] = manageremail

# now we have grabbed all the accounts we want to change the passwords from
# print "accounts to change password on:"
# print managedaccounts

# process command line args to get refine list of accounts to update..
if sys.argv[1] != "ALL":
   print "didnt get ALL, so processing cmdline args as list of ftp accounts"
   if sys.argv[1] == "NEW":
      # use new account email text, and take account list as 2nd cmd line param onwards.
      emailtext = newaccount
      ftpstoupdate = sys.argv[2:]
   else:
      # use password change email text, and take account list as 1st cmd line param onwards.
      emailtext = passwordchange
      ftpstoupdate = sys.argv[1:]

   for ftpaccount in managedaccounts.keys():
      if ftpaccount in ftpstoupdate:
         print "found configured account ",ftpaccount," in the commandline list"
      else:
         # print "didnt find ftp account ",ftpaccount," in cmdline list, skipping "
         del managedaccounts[ftpaccount]
else:
   emailtext = passwordchange

for ftpaccount, emails in managedaccounts.items():

   # generate password

   commandline = "/usr/bin/pwgen -ncA"
   process = subprocess.Popen(commandline, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
   newpassword = process.stdout.read().strip()

   # change password, check for success!
   commandline = "/usr/sbin/chpasswd"
   process = subprocess.Popen(commandline, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
   process.stdin.write("%s:%s\n" % (ftpaccount,newpassword)) 
   process.stdin.close()
   process.stdout.read()
   process.stdout.close()

   # if we didnt set the password, skip to next..
   if not process.poll() == 0:
      print "error setting password for account ",ftpaccount
      break

   # if successful, email credentials to list of recipients
   for email in emails:
      # place the veriables into the message text...
      message = emailtext % (sender,email,ftpaccount,ftpaccount,newpassword)

      # print "message is: ", message

      try:
         smtpObj = smtplib.SMTP('localhost')
         smtpObj.sendmail(sender, [email], message)
         print "   sent email to ",email," with new password ",newpassword," for ftp account ",ftpaccount
      except:
         print "Error: unable to send email to ",email

