from umqttsimple import MQTTClient
from machine import Pin, SoftSPI
from time import sleep
import machine
import ubinascii
import network
from sx127x import SX127x
from oled import *
import uhashlib
import ubinascii

SHA1 = uhashlib.sha1

KEY = b'foie_gras_celtic'

ssid = "INSA_RiSF"
password = "insa032023"
client_id = ubinascii.hexlify(machine.unique_id())
mqtt_server = "p-fb.net"
user_id = "insa"
user_pwd = "insa"
topic_sub = "duck"
topic_pub = "duck"
last_message = 0
message_interval = 5

device_config = {
    'miso': 19,
    'mosi': 27,
    'ss': 18,
    'sck': 5,
    'dio_0': 26,
    'reset': 14,
    'led': 25,
}
lora_parameters = {
    'frequency': 868E6,
    'tx_power_level': 10,
    'signal_bandwidth': 125E3,
    'spreading_factor': 11,
    'coding_rate': 5,
    'preamble_length': 8,
    'implicit_header': True,
    'sync_word': 0x12,
    'enable_CRC': True,
    'invert_IQ': False,
}


def sub_cb(topic, msg):
    print((topic, msg))
    if topic == b'notification' and msg == b'received':
        print('ESP received hello message')


def connect_and_subscribe():
    global client_id, user_id, user_pwd, mqtt_server, topic_sub
    client = MQTTClient(client_id=client_id, server=mqtt_server, port=6000, user=user_id, password=user_pwd)
    client.set_callback(sub_cb)
    client.connect()
    client.subscribe(topic_sub)
    print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
    return client


def restart_and_reconnect():
    print('Failed to connect to MQTT broker. Reconnecting...')
    time.sleep(10)
    # machine.reset()


def receiver(lora, oled, client):
    screen = ["  MSG Receive :", "", "", "", ""]
    if lora.received_packet():
        payload = lora.read_payload().decode("utf-8")
        msg = payload.split(":")[0]

        try:
            hmac = payload.split(":")[1]
        except IndexError:
            hmac = "no hmac"

        screen[2] = msg
        screen[3] = hmac
        if ubinascii.hexlify(HMAC(KEY, bytes(msg, "utf-8")).digest()).decode('utf-8') == hmac:
            screen[4] = "  Send To Server"
            client.publish(topic_sub, payload)
        else:
            screen[4] = "    Bad HMAC"
        write_screen(oled, screen)
        sleep(2)
        oled.fill(0)
        oled.show()

def HMAC(k, m):
    SHA1_BLOCK_SIZE = 64
    KEY_BLOCK = k + (b'\0' * (SHA1_BLOCK_SIZE - len(k)))
    KEY_INNER = bytes((x ^ 0x36) for x in KEY_BLOCK)
    KEY_OUTER = bytes((x ^ 0x5C) for x in KEY_BLOCK)
    inner_message = KEY_INNER + m
    outer_message = KEY_OUTER + SHA1(inner_message).digest()
    return SHA1(outer_message)

print("== Config LoRa ==")
device_spi = SoftSPI(baudrate=10000000,
                     polarity=0, phase=0, bits=8, firstbit=SoftSPI.MSB,
                     sck=Pin(device_config['sck'], Pin.OUT, Pin.PULL_DOWN),
                     mosi=Pin(device_config['mosi'], Pin.OUT, Pin.PULL_UP),
                     miso=Pin(device_config['miso'], Pin.IN, Pin.PULL_UP))

lora = SX127x(device_spi, pins=device_config, parameters=lora_parameters)
oled, screen = init_oled()
print("== Config WLAN ==")

station = network.WLAN(network.STA_IF)
if (not station.isconnected()):
    station.active(True)
    station.connect(ssid, password)
    while station.isconnected() == False:
        pass

print('Connection successful')
print(station.ifconfig())

print("== Config MQTT ==")
try:
    client = connect_and_subscribe()
except OSError as e:
    print(e)


while True:
    receiver(lora,oled,client)


