import sys

import RPi.GPIO as GPIO


GPIO.setwarnings(False)

_gpio_mode = GPIO.getmode()
if _gpio_mode is None:
    GPIO.setmode(GPIO.BCM)
elif _gpio_mode != GPIO.BCM:
    raise RuntimeError("limit_switch.py expects GPIO.BCM mode.")


LIMIT_SWITCH_ON = GPIO.LOW
LIMIT_SWITCH_OFF = GPIO.HIGH


def is_limit_switch_on(gpio_pin, configure_pin=True):
    """
    Read a limit switch wired with the Raspberry Pi internal pull-up resistor.

    OFF: the switch is open, so the pin is pulled HIGH and current does not flow to GND.
    ON: the switch is closed, so the pin is connected to GND and reads LOW.

    Args:
        gpio_pin: BCM GPIO pin connected to the limit switch.
        configure_pin: If True, set the pin up as an input with GPIO.PUD_UP before reading.

    Returns:
        True when the switch is ON and conducting to GND, otherwise False.
    """
    if configure_pin:
        GPIO.setup(gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    return GPIO.input(gpio_pin) == LIMIT_SWITCH_ON


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 limit_switch.py <bcm_gpio_pin>")
        raise SystemExit(1)

    gpio_pin = int(sys.argv[1])

    try:
        state = "ON" if is_limit_switch_on(gpio_pin) else "OFF"
        print(f"Limit switch on GPIO {gpio_pin} is {state}")
    finally:
        GPIO.cleanup(gpio_pin)


if __name__ == "__main__":
    main()
