Pytilt
==========
Tool for reading your Tilt brewing hydrometer[1] in python and exporting the data over MQTT as a json object


Installation
------------
1. git clone https://github.com/edman007/pytilt.git
2. Install python3-bluez and mqtt: ```sudo apt-get install python3-bluez python3-paho-mqtt```
3. Edit the MQTT config parameters in pytilt.py (if not localhost)

Running
-----------
1. From the directory containing pytilt.py run `sudo python3 pytilt.py`

Running Pytilt in the background and on System Start
-----------
1. edit pytilt.service, correct the path to wherever you have the repo, and set a user (not root) that can access that path
2. copy pytilt.service to /etc/systemd/system/
3. sudo chmod 644 /etc/systemd/system/pytilt.service && sudo chown root:root /etc/systemd/system/pytilt.service
4. sudo systemctl daemon-reload
5. sudo systemctl enable pytilt.service


Acknowledgements
----------------
The code in blescan-py is adapted from https://github.com/switchdoclabs/iBeacon-Scanner-
The Tilt UUID-to-color mapping is taken from: https://github.com/tbryant/brewometer-nodejs
Systemd-config here: http://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd/


[1]: https://tilthydrometer.com/
