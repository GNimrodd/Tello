import IPython
from tello2 import DroneController
from typing import Dict, Callable, Any
from keyboard_controll2 import KeyboardControl
import logging

DRONES = {"Frodo": "TELLO-579043",
          "Sam": "TELLO-578FDA"}


def main():
    logging.root.setLevel(logging.DEBUG)
    drone = DroneController(ssid=DRONES['Frodo'])
    drone.arm()
    drone.streamon()
    KeyboardControl(drone, camera=drone.stream).pass_control()
    drone.end()


if __name__ == "__main__":
    main()
