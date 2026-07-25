from machine import Pin, PWM
from time import sleep

servo = PWM(Pin(15))
servo.freq(50)

def mover(pulso_us):
    duty = int(pulso_us * 65535 / 20000)
    servo.duty_u16(duty)

while True:
    print("0 graus")
    mover(500)
    sleep(2)

    print("90 graus")
    mover(1500)
    sleep(2)

    print("180 graus")
    mover(2500)
    sleep(2)