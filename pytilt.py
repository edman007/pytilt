import sys
import datetime
import time

import bluetooth._bluetooth as bluez

import blescan
from sender import Sender


TILTS = {
        'a495bb10c5b14b44b5121370f02d74de': 'Red',
        'a495bb20c5b14b44b5121370f02d74de': 'Green',
        'a495bb30c5b14b44b5121370f02d74de': 'Black',
        'a495bb40c5b14b44b5121370f02d74de': 'Purple',
        'a495bb50c5b14b44b5121370f02d74de': 'Orange',
        'a495bb60c5b14b44b5121370f02d74de': 'Blue',
        'a495bb70c5b14b44b5121370f02d74de': 'Yellow',
        'a495bb80c5b14b44b5121370f02d74de': 'Pink',
}

MQTT_BROKER='localhost'
MQTT_TOPIC='tilt'

def distinct(objects):
    seen = set()
    unique = []
    for obj in objects:
        if obj['uuid'] not in seen:
            unique.append(obj)
            seen.add(obj['uuid'])
    return unique


def monitor_tilt():
    sender = Sender(MQTT_BROKER, MQTT_TOPIC)
    while True:
        beacons = distinct(blescan.parse_events(sock, 10))
        for beacon in beacons:
            if beacon['uuid'] in TILTS.keys():
                #print(beacon)
                sender.add_data({
                    'color': TILTS[beacon['uuid']],
                    'timestamp': datetime.datetime.now().isoformat(),
                    'temp': beacon['major'],
                    'gravity': beacon['minor']/1000,
                    'rssi': beacon['rssi'],
                    'tx_power': beacon['tx_power']
                })
        time.sleep(30)


if __name__ == '__main__':
    dev_id = 0
    try:
        sock = bluez.hci_open_dev(dev_id)
        print ('Starting pytilt logger')
    except:
        print ('error accessing bluetooth device...')
        sys.exit(1)

    blescan.hci_le_set_scan_parameters(sock)
    blescan.hci_enable_le_scan(sock)
    monitor_tilt()
