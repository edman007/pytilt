# based on https://github.com/switchdoclabs/iBeacon-Scanner-

import os
import sys
import struct
import bluetooth._bluetooth as bluez

LE_META_EVENT = 0x3e
LE_PUBLIC_ADDRESS = 0x00
LE_RANDOM_ADDRESS = 0x01
LE_SET_SCAN_PARAMETERS_CP_SIZE = 7
OGF_LE_CTL = 0x08
OCF_LE_SET_SCAN_PARAMETERS = 0x000B
OCF_LE_SET_SCAN_ENABLE = 0x000C
OCF_LE_CREATE_CONN = 0x000D

LE_ROLE_MASTER = 0x00
LE_ROLE_SLAVE = 0x01

# these are actually subevents of LE_META_EVENT
EVT_LE_CONN_COMPLETE = 0x01
EVT_LE_ADVERTISING_REPORT = 0x02
EVT_LE_CONN_UPDATE_COMPLETE = 0x03
EVT_LE_READ_REMOTE_USED_FEATURES_COMPLETE = 0x04

# Advertisment event types
ADV_IND = 0x00
ADV_DIRECT_IND = 0x01
ADV_SCAN_IND = 0x02
ADV_NONCONN_IND = 0x03
ADV_SCAN_RSP = 0x04


def returnnumberpacket(pkt):
    if (len(pkt) == 2):
        return int(struct.unpack('>H', pkt)[0])
    if (len(pkt) == 1):
        return int(struct.unpack('b', pkt)[0])
    print(pkt.hex())
    print('unknown pkt size' + str(len(pkt)))
    return 0


def returnstringpacket(pkt):
    return pkt.hex()


def printpacket(pkt):
    for c in pkt:
        sys.stdout.write('%02x ' % struct.unpack('B', bytes(c)[0:1])[0])


def get_packed_bdaddr(bdaddr_string):
    packable_addr = []
    addr = bdaddr_string.split(':')
    addr.reverse()
    for b in addr:
        packable_addr.append(int(b, 16))
    return struct.pack('<BBBBBB', *packable_addr)


def packed_bdaddr_to_string(bdaddr_packed):
    return ':'.join('%02x' % i for i in struct.unpack("<BBBBBB", bdaddr_packed[::-1]))


def hci_enable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x01)


def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x00)


def hci_toggle_le_scan(sock, enable):
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)


def hci_le_set_scan_parameters(sock):
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    SCAN_RANDOM = 0x01
    OWN_TYPE = SCAN_RANDOM
    SCAN_TYPE = 0x01


def parse_events(sock, loop_count=100):
    old_filter = sock.getsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, 16)
    # perform a device inquiry on bluetooth device #0
    # The inquiry should last 8 * 1.28 = 10.24 seconds
    # before the inquiry is performed, bluez should flush its cache of
    # previously discovered devices
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, flt)
    beacons = []
    for i in range(0, loop_count):
        pkt = sock.recv(255)
        # print(pkt.hex())
        # 043e2a0201030 11c15ce68a6e91e020104 1a ff4c 000215 a495bb70c5b14b44b5121370f02d74de 003a 03fb c5bc
        # 043e2a0201030 028679978d2b01e020106 1a ff4c 000215 54616130db3a50e4bd5b485627a7331c 0000 0000 c59c
        ptype, event, plen = struct.unpack('BBB', bytes(pkt[:3]))
        if event == LE_META_EVENT:
            subevent, = struct.unpack('B', bytes(pkt[3:4]))
            pkt = pkt[4:]
            if subevent == EVT_LE_CONN_COMPLETE:
                le_handle_connection_complete(pkt)
                print('close')
            elif subevent == EVT_LE_ADVERTISING_REPORT:
                raw_report = struct.unpack('B', bytes(pkt[0:1]))
                num_reports = raw_report[0]
                report_pkt_offset = 0
                for i in range(0, num_reports):
                    beacons.append({
                        'raw': pkt.hex(),
                        'uuid': returnstringpacket(pkt[report_pkt_offset - 22: report_pkt_offset - 6]),
                        'minor': returnnumberpacket(pkt[report_pkt_offset - 4: report_pkt_offset - 2]),
                        'major': returnnumberpacket(pkt[report_pkt_offset - 6: report_pkt_offset - 4]),
                        'tx_power': returnnumberpacket(pkt[report_pkt_offset - 2: report_pkt_offset - 1]),
                        'rssi': returnnumberpacket(pkt[-1:])
                    })
                done = True
    sock.setsockopt(bluez.SOL_HCI, bluez.HCI_FILTER, bytes(old_filter))
    return beacons
