ftp_change_password
===================

script to change passwords for a set of unix shell ftp accounts and email the passwords to a list of recipients per account.
Presumes airly standard (Debian Linux etc) ftp accounts as unix shell accounts, email sent via smtp to localhost, etc.

Can be run on the command line, or scripted to be run from CRON.

The list of email addresses for each account is configured in the Unix/Linux /etc/passwd file, and is done
for accounts that hold the marker FTPMANAGER followed by a list of valid emails.

If the command is run with command line arg ALL it changes the password for all configured accounts,
sending the password change text.

If it is run with the command line arg NEW it sends the "new ftp account" text for the accounts provided on the command line.

