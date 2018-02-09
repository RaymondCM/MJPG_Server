# MJPEG Camera Server

Provides an interface to stream camera devices over an ethernet socket and preview them in most modern browsers. 
Supports the following devices [Lepton3 FLIR Camera](https://groupgets.com/manufacturers/flir/products/lepton-3-0), 
[Raspberry PI Cameras](https://www.raspberrypi.org/products/camera-module-v2/) and almost all USB plug and play web-cams
and inbuilt devices supported by [OpenCV](https://opencv.org/).

## Quick start

Run the server on the camera device host.

```bash
usage: server.py [-h] [-b IP] [-p PORT] [-d DEVICE]

optional arguments:
  -h, --help  show this help message and exit
  -b IP       Server IP Address [Default 0.0.0.0]
  -p PORT     Server Port [Default: 8080]
  -d DEVICE   Device Type [Default:auto] (pi|lepton|cv)
```

Run the client python script on any other machine on the network to preview the camera. 
Alternatively go-to http://192.168.0.XXX:8080/index.html in any modern browser (Change the port and IP accordingly). 
Support for publishing to a ros node has been added also via a command line argument -r.

```bash
usage: client.py [-h] [-b IP] [-p PORT] [-w WAIT] [-c BSIZE] [-n NAME]
                 [-r ROS_SUP]

optional arguments:
  -h, --help  show this help message and exit
  -b IP       Server IP Address [Default 127.0.0.1]
  -p PORT     Server Port [Default: 8080]
  -w WAIT     Wait for frame [Default: False]
  -c BSIZE    Byte chunk size [Default: 2048]
  -n NAME     Node name [Default: auto]
  -r ROS_SUP  Publish on ros node [Default: False]
```

## Installation

To use the FLIR thermal camera run the following command in the project root (Supports Lepton3 only).

```bash
cd MJPG_Server
git clone https://github.com/RaymondKirk/pylepton.git --depth 1
```

To use the pi-camera ensure the package is installed and up to-date. 

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-picamera
```

To use USB camera devices or in-built ones, or to use the client python script, install [OpenCV](https://opencv.org/).

```bash
pip install opencv-python
```

## Raspberry Pi Setup

To setup on a Raspberry Pi, follow these instructions [Raspberry Pi Setup](./docs/raspberry_pi_setup.md).