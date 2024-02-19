from machine import Pin
def handle_interrupt(pin):
    print("bouton !")


bouton = Pin(0, Pin.IN)
bouton.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)