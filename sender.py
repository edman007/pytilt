# -*- coding: utf-8 -*-
import requests
import json
from multiprocessing import Pool
import time
import os
import paho.mqtt.client as mqtt




class Sender(object):

    def __init__(self, broker, topic, port=1883):
        self.queue = []
        self.sending = []
        self.broker = broker
        self.topic = topic
        self.port = port
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        status = self.client.connect(self.broker, self.port)
        self.client.loop_start()

    def add_data(self, data):
        self.queue.append(data)
        self.send()

    def sendMessage(self, data):
        try:
            if (not self.client.is_connected()):
                print('Not Sending')
                return False
            result = self.client.publish(self.topic, json.dumps(data))
            status = result[0]
            if status != mqtt.MQTT_ERR_SUCCESS:
                print(f"Failed to send message to topic {self.topic}, status code: {status}")
            #else:
            #    print(f"Sent to topic `{self.topic}`")

            return status == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            print(f"Failed to send message to broker: {e}")
            return False

    def send(self):
        self.sending = list(self.queue)
        self.queue = []
        for message in self.sending:
            if (self.sendMessage(message)):
                continue
            else:
                #add message back to queue
                self.queue += message
                try:
                    self.client.disconnect()
                    self.client.reconnect()
                    self.client.loop_start()
                except Exception as e:
                    print(f"Failed to reconnect to broker: {e}")
                #give up if we have an excessive number added back on
                if len(self.queue) > 100:
                    self.queue = []

