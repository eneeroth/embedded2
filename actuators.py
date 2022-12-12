
import RPi.GPIO as GPIO
import time
import threading


def controller_larm():
    global reset
    reset = False
    larm_thread = threading.Thread(target=larm)
    larm_thread.start()

    input('Press enter to reset')
    reset = True


def larm(on=False):
    """ Buzzer and red led blink"""
    global reset

    BUZZER = 12
    LED_RED = 11
    LED_YELLOW = 13
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(BUZZER, GPIO.OUT)
    GPIO.setup(LED_RED, GPIO.OUT)
    GPIO.setup(LED_YELLOW, GPIO.OUT)
    #GPIO.setwarnings(False)

    counter = 0
    if not reset:
        GPIO.output(LED_RED, GPIO.HIGH)
        while not reset:
            #GPIO.output(BUZZER, GPIO.HIGH)
            #print("Beep")
            time.sleep(0.2)
            #GPIO.output(BUZZER, GPIO.LOW)
            #GPIO.output(LED_RED, GPIO.LOW)
            #print("No Beep")
            time.sleep(0.2)

        GPIO.cleanup()

    else:
        GPIO.output(BUZZER, GPIO.LOW)        
        GPIO.cleanup()
    




def warning_led(on=True):
    """ led light to warn high temp"""
    LED_PIN = 13
    LED_RED = 11
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LED_PIN, GPIO.OUT)
    #GPIO.setup(LED_RED, GPIO.OUT)
   
    if on:
        GPIO.output(LED_PIN, GPIO.HIGH)
    else:
        GPIO.output(LED_PIN, GPIO.LOW)


if __name__ == '__main__':
    warning_led()
    #larm(on=True)
    time.sleep(2)
    warning_led(on=False)
    #larm(on=False)
    #GPIO.cleanup()

    controller_larm()
