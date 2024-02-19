from umqttsimple import MQTTClient

import machine
import ubinascii
import network
from sx127x import SX127x
from oled import *

ssid = "INSA_RiSF"
password = "insa032023"
client_id = ubinascii.hexlify(machine.unique_id())
mqtt_server = "serveur.iot.com"
user_id = "esp32"
user_pwd = "esp32"
topic_sub = "vers_esp32"
topic_pub = "depuis_esp32"
last_message = 0
message_interval = 5
counter = 0


def sub_cb(topic, msg):
    print((topic, msg))
    if topic == b'notification' and msg == b'received':
        print('ESP received hello message')


def connect_and_subscribe():
    global client_id, user_id, user_pwd, mqtt_server, topic_sub
    client = MQTTClient(client_id=client_id, server=mqtt_server, port=1883, user=user_id, password=user_pwd)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client


def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    # machine.reset()


station = network.WLAN(network.STA_IF)
if (not station.isconnected()):
    station.active(True)
    station.connect(ssid, password)
    while station.isconnected() == False:
        pass

print('Connection successful')
print(station.ifconfig())
try:
    client = connect_and_subscribe()


except OSError as e:
    restart_and_reconnect()
while True:
    try:
        client.check_msg()
        if (time.time() - last_message) > message_interval:
            msg = b'Hello #%d' % counter
            client.publish(topic_pub, msg)
            last_message = time.time()
            counter += 1


    except OSError as e:
        restart_and_reconnect()
