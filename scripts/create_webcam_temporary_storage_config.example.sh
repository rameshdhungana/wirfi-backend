#!/home/insightworkshop/wirfi-venv/bin/python3

import configparser

config = configparser.ConfigParser()
config['webcamTemporaryStorageLocation'] ={'storageLocation':'/home/insightworkshop/IwProjects/Projects/wirfi-web/media/webcam-videos/'}


# Writing our configuration file to 'webcamTemporaryStorageLocation.cfg'
with open('webcamTemporaryStorageLocation.cfg', 'w') as configfile:
    config.write(configfile)

