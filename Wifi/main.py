import network
import time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect('INSA_RiSF', 'insa032023')
    time.sleep(500)
print('network config:', wlan.ifconfig())