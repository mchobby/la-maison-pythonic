#!/bin/sh -

# This script initialize the needed software parts to run sqlite3
# database storage & dashboard Flask App

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

echo "Install dashboard.ini to /etc/pythonic/"
# file in /etc/pythonic/dashboard.ini can be read by user pi
sudo mkdir /etc/pythonic
# The default configuration is read from the app directory
# sudo cp config.sample /etc/pythonic/dashboard.cfg

echo "Install dashboard.log in /var/log/pythonic/"
sudo mkdir /var/log/pythonic
sudo chgrp staff /var/log/pythonic
sudo chmod g+rw /var/log/pythonic

# reload user and group 
exec su -l $USER

# owner and group  would be the current user (pi)
touch /var/log/pythonic/dashboard.log
# Set permission to -rw-rw-r--
sudo chmod +664 /var/log/pythonic/dashboard.log
# change owner to root (keep pi as the group)
sudo chown root /var/log/pythonic/dashboard.log

echo "Creating dashboard.db in var/local/sqlite/"
# Initialize the pythonic dashboard databases to run the dashboard
# flask App. That App read the MQTT data stored in the push-to-db.db
# database
cat createdb.sql | sqlite3 /var/local/sqlite/dashboard.db

echo "Installing python libraries"
sudo pip install paho-mqtt

echo "Done!"

