# Installation instructions for the Raspberry Pi

# Installation
Install the necessary dependencies, some are optional.

```bash
cd MJPG_Server
git clone https://github.com/RaymondKirk/pylepton.git --depth 1
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-picamera
pip install opencv-python
```
# Running on startup

- Create a bash script to run the server(s). For example you can use the one below to run and terminate the python servers correctly. Remember to comment the '...starting python thermal...' lines out when the camera doesnt exist.

```bash
#!/bin/bash

function finish() {
kill -- -$$
echo "Killing both processes for good measure"
ps aux | grep '[s]erver.py'
kill $(ps aux | grep '[s]erver.py' | awk '{print $2}')
ps aux | grep '[s]erver.py'
}

trap "trap - SIGTERM && finish" SIGINT SIGTERM EXIT
FAIL=0

echo "Starting Python PiCamera Server Process"
/usr/bin/python /home/pi/MJPG_Server/server.py -d pi > /home/pi/MJPG_Server/server_pi.log 2>&1 &

echo "Starting Python Thermal Server Process"
/usr/bin/python /home/pi/MJPG_Server/server.py -p 8081 -d lepton > /home/pi/MJPG_Server/server_lepton.log 2>&1 &

for job in `jobs -p`
do
echo $job
    wait $job || let "FAIL+=1"
done

echo $FAIL

if [ "$FAIL" == "0" ];
then
echo "Both server processes exited cleanly!"
else
echo "Server processes did not exit cleanly! Error count($FAIL)"
fi
```

- Create a ```systemmd``` service that will be run on boot.

```bash
sudo nano /lib/systemd/system/mjpgserver.service
```

- Enter the following text, replacing the bash file with the one you created.

```text
[Unit]
Description=Motion JPEG Server Autostart
After=multi-user.target

[Service]
Type=idle
ExecStart=/bin/bash /home/pi/pi_server.sh > /home/pi/server_bash.log 2>&1
Restart=always

[Install]
WantedBy=multi-user.target
```

- Configure the service to start at boot

```bash
sudo chmod 644 /lib/systemd/system/mjpgserver.service
sudo systemctl daemon-reload
sudo systemctl enable mjpgserver.service
sudo reboot
```