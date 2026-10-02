import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

GPIO.setwarnings(False)
rfid = SimpleMFRC522()
counter = 0

try:
    while True:
        counter += 1
        print("Tap card...")
        card_id, text = rfid.read()
        print(f"Count: {counter}")
        print(f"ID   : {card_id}")
        print(f"Text : {text}")
except KeyboardInterrupt:
    print("\nProgram dihentikan.")
finally:
    GPIO.cleanup()
