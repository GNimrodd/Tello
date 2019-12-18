from enum import Enum
from typing import NamedTuple, Any
import logging
import numpy as np
import threading
import socket
import winwifi
import sys
import cv2
from opencvutils.Camera import CameraCV
from videostream import CameraStream


class Vec3D:
    def __init__(self, x=None, y=None, z=None):
        self.x: int = x
        self.y: int = y
        self.z: int = z


class IMU(NamedTuple):
    pitch: int
    roll: int
    yaw: int


class TelloResponse(Enum):
    OK = 0
    ERROR = 1


class DroneController:
    """
    A drone representation.
    Saves drone data
    """

    logger = logging.getLogger("DroneLogger")

    TELLO_ADDRESS = ('192.168.10.1', 8889)
    LOCAL_ADDRESS = ('', 9000)
    VIDEO_ADDRESS = ('', 11111)

    def __init__(self, tello_wifi: str):
        self.tello_wifi = tello_wifi
        self.armed = False
        self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.stream = None
        self.battery = 0

    @classmethod
    def set_debug(cls):
        logging.getLogger().setLevel(logging.DEBUG)

    def help(self):
        print('\n'.join(self.__dict__.keys()))

    def arm(self) -> "DroneController":
        self.logger.debug(f"Conneting to wifi: {self.tello_wifi}")
        winwifi.WinWiFi.connect(self.tello_wifi)
        self.armed = True
        self.logger.debug("Binding sockets")
        self.command_socket.bind(self.LOCAL_ADDRESS)
        self.logger.debug("Arming...")
        self._send_command("command")
        self.get_battery()
        return self

    def streamon(self):
        self._send_command("streamon")
        self.stream = CameraStream(f"{self.tello_wifi}")
        self.stream.start()

    def streamoff(self):
        self._send_command("streamoff")
        self.stream.stop()
        self.stream.join()

    def shutdown(self):
        self.command_socket.close()

    def takeoff(self):
        self._send_command("takeoff")

    def land(self):
        self._send_command("land")

    def emergency(self):
        self._send_command("emergency")

    class MoveControl:
        def __init__(self, drone: "DroneController"):
            self.drone = drone

        def up(self, x: int):
            if x < 20 or x > 500:
                raise ValueError(f"Illegal value: {x}")
            self.drone._send_command(f"up {x}")

        def down(self, x: int):
            if x < 20 or x > 500:
                raise ValueError(f"Illegal value: {x}")
            self.drone._send_command(f"down {x}")

        def left(self, x: int):
            if x < 20 or x > 500:
                raise ValueError(f"Illegal value: {x}")
            self.drone._send_command(f"left {x}")

        def right(self, x: int):
            if x < 20 or x > 500:
                raise ValueError(f"Illegal value: {x}")
            self.drone._send_command(f"right {x}")

        def forward(self, x: int):
            if x < 20 or x > 500:
                raise ValueError(f"Illegal value: {x}")
            self.drone._send_command(f"forward {x}")

        def back(self, x: int):
            if x < 20 or x > 500:
                raise ValueError(f"Illegal value: {x}")
            self.drone._send_command(f"back {x}")

    @property
    def move(self):
        return DroneController.MoveControl(self)

    class RotateControl:
        def __init__(self, drone: "DroneController"):
            self.drone = drone

        def cw(self, x: int):
            if x < 1 or x > 3600:
                raise ValueError(f"Illegal value: {x}")
            self.drone._send_command(f"cw {x}")

        def ccw(self, x: int):
            if x < 1 or x > 3600:
                raise ValueError(f"Illegal value: {x}")
            self.drone._send_command(f"ccw {x}")

    @property
    def rotate(self):
        return DroneController.RotateControl(self)

    class FlipControl:
        def __init__(self, drone: "DroneController"):
            self.drone = drone

        def back(self):
            self._flip('b')

        def right(self):
            self._flip('r')

        def left(self):
            self._flip('l')

        def forward(self):
            self._flip('f')

        def _flip(self, direction: str):
            self.drone._send_command(f"flip {direction}")

    @property
    def flip(self):
        return DroneController.FlipControl(self)

    def go(self, p: Vec3D, speed: int):
        self._send_command(f"go {p.x} {p.y} {p.z} {speed}")

    def curve(self, p1: Vec3D, p2: Vec3D, speed: int):
        self._send_command(f"curve {p1.x} {p2.x} {p1.y} {p2.y} {p1.z} {p2.z} {speed}")

    def set_speed(self, x: int):
        self._send_command(f"speed {x}")

    def set_rc(self, left_right: int, forward_backward: int, up_down: int, yaw: int):
        self._send_command(f"rc {left_right} {forward_backward} {up_down} {yaw}")

    def set_wifi_ssid(self, ssid: int, password: str):
        self._send_command(f"wifi {ssid} {password}")

    def get_speed(self) -> int:
        return int(self._send_command("speed?"))

    def get_battery(self) -> int:
        self.battery = int(self._send_command("battery?"))
        return self.battery

    def get_time(self) -> int:
        return int(self._send_command("time?"))

    def get_height(self) -> int:
        return int(self._send_command("height?"))

    def get_temp(self) -> int:
        return int(self._send_command("temp?"))

    def get_attitude(self) -> IMU:
        self._send_command("attitude?")

    def get_barometric(self) -> int:
        return int(self._send_command("baro?"))

    def get_acceleration(self) -> Vec3D:
        return Vec3D(*[int(x) for x in self._send_command("acceleration?").split()])

    def get_tof(self) -> int:
        return self._send_command("tof?")

    def get_wifi(self) -> TelloResponse:
        return TelloResponse.OK if self._send_command("wifi?") == "ok" else TelloResponse.ERROR

    def _send_command(self, cmd: str) -> Any:
        self.logger.debug(cmd)
        self.command_socket.sendto(cmd.encode(encoding="utf-8"), self.TELLO_ADDRESS)
        data = 0
        try:
            data = self.command_socket.recvfrom(1518)[0].decode(encoding="utf-8")
            self.logger.debug(data)
        except Exception as e:
            print(e)
        return data

    def __repr__(self):
        return f"<{self.__class__.__name__}: id={self.tello_wifi} armed={self.armed} battery={self.battery}>"


def assert_armed(func):
    def new_func(drone: DroneController):
        assert drone.armed, "Drone isn't connected"
        return func(drone)

    return new_func


@assert_armed
def test_motion(drone: DroneController):
    drone.move.up(30)
    drone.move.right(30)
    drone.move.left(30)
    drone.move.down(30)


@assert_armed
def test_flip(drone: DroneController):
    drone.flip.back()
    drone.flip.forward()
    drone.flip.right()
    drone.flip.left()


Frodo = "TELLO-579043"
Sam = "TELLO-578FDA"
DRONES = {"Frodo": Frodo, "Sam": Sam}


def main():
    DroneController.logger.setLevel(logging.DEBUG)
    DroneController.set_debug()
    d = DroneController(Frodo)
    d.arm()
    try:
        d.streamon()
        # if d.get_battery() < 30:
        #     print(f"battery low: {d.battery}, charge and test again later")
        # else:
        #     d.takeoff()
        #     test_motion(d)
        #     test_flip(d)
    finally:
        d.land()
    d.shutdown()


if __name__ == '__main__':
    main()
