from machine import Pin, SoftSPI
from time import sleep
from sx127x import SX127x
from oled import *
import machine
import uhashlib
import ubinascii

SHA1 = uhashlib.sha1
KEY = b'foie_gras_celtic'
counter = 0
file = open("./rockyou.txt", "r")

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

def HMAC(k, m):
    SHA1_BLOCK_SIZE = 64
    KEY_BLOCK = k + (b'\0' * (SHA1_BLOCK_SIZE - len(k)))
    KEY_INNER = bytes((x ^ 0x36) for x in KEY_BLOCK)
    KEY_OUTER = bytes((x ^ 0x5C) for x in KEY_BLOCK)
    inner_message = KEY_INNER + m
    outer_message = KEY_OUTER + SHA1(inner_message).digest()
    return SHA1(outer_message)

def send(lora, oled):
    msg = file.readline().strip()
    screen = [" ", msg, " ", " "]
    hmac = ubinascii.hexlify(HMAC(KEY, bytes(msg, "utf-8")).digest()).decode('utf-8')
    payload = msg + ':' + hmac
    write_screen(oled, screen)
    lora.println(payload)
    sleep(1)
    oled.fill(0)
    oled.show()


device_spi = SoftSPI(baudrate=10000000,
                     polarity=0, phase=0, bits=8, firstbit=SoftSPI.MSB,
                     sck=Pin(device_config['sck'], Pin.OUT, Pin.PULL_DOWN),
                     mosi=Pin(device_config['mosi'], Pin.OUT, Pin.PULL_UP),
                     miso=Pin(device_config['miso'], Pin.IN, Pin.PULL_UP))

lora = SX127x(device_spi, pins=device_config, parameters=lora_parameters)
oled, screen = init_oled()

bouton = machine.Pin(0, machine.Pin.IN)
bouton.irq(trigger=machine.Pin.IRQ_RISING, handler=lambda pin: send(lora, oled))

while True:

    sleep(0.1)
