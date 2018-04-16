#!/bin/sh -

# This script initialize the needed software parts to run sqlite3
# database storage & push-to-db.py script

echo "Install SQLite3"
sudo apt-get install sqlite

echo "Create storage path /var/local/sqlite"
sudo mkdir /var/local/sqlite
# /var/local is owned by root and accessible to group staff
# so /var/local/sqlite should also do so.

echo "Add user 'pi' to group 'staff'"
sudo usermod -a -G staff pi
echo "Set 'staff' as group for 'sqlite' folder"
sudo chgrp staff /var/local/sqlite
echo "Give right to group 'staff' on 'sqlite' folder"
sudo chmod g+rwx /var/local/sqlite

echo "Install push-to-db.ini to /etc/pythonic/"
# file in /etc/pythonic/push-to-db.ini can be read by user pi
sudo mkdir /etc/pythonic
sudo cp inifile.sample /etc/pythonic/push-to-db.ini

echo "Install push-to-db.log in /var/log/pythonic/"
sudo mkdir /var/log/pythonic
sudo chgrp staff /var/log/pythonic
sudo chmod g+rw /var/log/pythonic
# owner and group  would be the current user (pi)
touch /var/log/pythonic/push-to-db.log
# Set permission to -rw-rw-r--
sudo chmod +664 /var/log/pythonic/push-to-db.log
# change owner to root (keep pi as the group)
sudo chown root /var/log/pythonic/push-to-db.log

echo "Creating pythonic.db in var/local/sqlite/"
# Initialize the pythonic databases to run the push-to-db.py python script. 
# push-to-db.py push MQTT data to SQLite3 database
cat createdb.sql | sqlite3 /var/local/sqlite/pythonic.db

echo "Installing python libraries"
sudo pip install paho-mqtt

echo "Done!"

