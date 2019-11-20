from enum import Enum
from typing import NamedTuple, List
import logging
import numpy as np
import threading
import socket
import libh264decoder


class Point3D(NamedTuple):
    x: int
    y: int
    z: int


class IMU(NamedTuple):
    pitch: int
    roll: int
    yaw: int


class TelloResponse(Enum):
    OK = 0
    ERROR = 1


class Drone:
    """
    A drone representation
    """

    DroneLog = logging.getLogger("Drone")

    TELLO_ADDRESS = ('192.168.10.1', 8889)
    LOCAL_ADDRESS = ('', 9000)
    LOCAL_VIDEO = ('', 1111)

    def __init__(self):
        self.is_connected = False
        self.sock = None
        self.video_sock = None
        self.video_thread = threading.Thread(target=self._recieve_video, daemon=True)

    def help(self):
        print('\n'.join(self.__dict__.keys()))

    def arm(self):
        self.is_connected = True
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.LOCAL_ADDRESS)
        self._send_command("command")

    def shutdown(self):
        self.sock.close()

    def takeoff(self):
        self._send_command("takeoff")

    def land(self):
        self._send_command("land")

    def _h264_decode(self, packet_data):
        res_frame_list = []
        frames = self.decoder.decode(packet_data)
        for framedata in frames:
            (frame, w, h, ls) = framedata
            if frame is not None:
                frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
                frame = (frame.reshape((h, ls / 3, 3)))
                frame = frame[:, :w, :]
                res_frame_list.append(frame)

        return res_frame_list

    def _recieve_video(self):
        packet_data = ""
        while True:
            res_string, ip = self.video_sock.recvfrom(2048)
            packet_data += res_string
            if len(res_string) != 1460:
                for frame in self._h264_decode(packet_data):
                    self.frame = frame
                packet_data = ""


    def streamon(self):
        self._send_command("streamon")
        self.video_thread.start()

    def streamoff(self):
        self._send_command("streamoff")

    def emergency(self):
        self._send_command("emergency")

    def up(self, x: int):
        self._send_command(f"up {x}")

    def down(self, x: int):
        self._send_command(f"down {x}")

    def left(self, x: int):
        self._send_command(f"left {x}")

    def right(self, x: int):
        self._send_command(f"right {x}")

    def forward(self, x: int):
        self._send_command(f"forward {x}")

    def back(self, x: int):
        self._send_command(f"back {x}")

    def rotate_clockwise(self, x: int):
        self._send_command(f"cw {x}")

    def rotate_counter_clockwise(self, x: int):
        self._send_command(f"ccw {x}")

    def _flip(self, direction: str):
        self._send_command(f"flip {direction}")

    def flipback(self):
        self._flip('b')

    def flipright(self):
        self._flip('r')

    def flipleft(self):
        self._flip('l')

    def flipforward(self):
        self._flip('f')

    def go(self, p: Point3D, speed: int):
        self._send_command(f"go {p.x} {p.y} {p.z} {speed}")

    def curve(self, p1: Point3D, p2: Point3D, speed: int):
        self._send_command(f"curve {p1.x} {p2.x} {p1.y} {p2.y} {p1.z} {p2.z} {speed}")

    def set_speed(self, x: int):
        self._send_command(f"speed {x}")

    def set_rc(self, left_right: int, forward_backward: int, up_down: int, yaw: int):
        self._send_command(f"rc {left_right} {forward_backward} {up_down} {yaw}")

    def set_wifi_ssid(self, ssid: int, password: str):
        self._send_command(f"wifi {ssid} {password}")

    def get_speed(self) -> int:
        self._send_command("speed?")

    def get_battery(self) -> int:
        self._send_command("battery?")

    def get_time(self) -> int:
        self._send_command("time?")

    def get_height(self) -> int:
        self._send_command("height?")

    def get_temp(self) -> int:
        self._send_command("temp?")

    def get_attitude(self) -> IMU:
        self._send_command("attitude?")

    def get_barometric(self) -> int:
        self._send_command("baro?")

    def get_acceleration(self) -> Point3D:
        self._send_command("acceleration?")

    def get_tof(self) -> int:
        self._send_command("tod?")

    def get_wifi(self):
        self._send_command("wifi?")

    def _send_command(self, cmd: str):
        print(cmd)
        self.sock.sendto(cmd.encode(encoding="utf-8"), self.TELLO_ADDRESS)
        data, _ = self.sock.recvfrom(1518)
        print(data.decode(encoding="utf-8"))


if __name__ == '__main__':
    d = Drone()
    d.arm()
    d.takeoff()
    d.get_height()
    d.flipback()
    d.get_battery()
    d.land()
    d.shutdown()
