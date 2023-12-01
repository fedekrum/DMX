# DMX

All my experience on making the chipest DMX setup for theater plays on a my Mac.

## Harware

ESPixelstick 4 beta
Node MCU
Instalacion con java -jar xxxxxxx

## Software

PyArtnet (usando E1.31)
https://github.com/spacemanspiff2007/PyArtNet
python3 scanDMX.py -a192.168.188.81 -u1 -c1 -r10 -s500 -k

python3 scanDMX.py
usage: scanDMX.py [-h] -a ADDRESS -u UNIVERSE [-c CHANNEL] [-r RANGE] [-s SPEED] [-k]
