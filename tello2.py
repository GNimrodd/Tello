from enum import Enum
from typing import NamedTuple, Any
from utils import generate_logger, connect_wifi
import socket
from camera_stream import CameraStream


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

    LOGGER = generate_logger("DroneLogger")

    TELLO_ADDRESS = ('192.168.10.1', 8889)
    LOCAL_ADDRESS = ('', 9000)
    VS_UDP_IP = '0.0.0.0'
    VS_UDP_PORT = 11111

    def __init__(self, ssid: str, **kwargs):
        if not connect_wifi(ssid):
            raise OSError(f"Failed to connect to wifi {ssid}")
        self.udp_address = 'udp://@' + self.VS_UDP_IP + ':' + str(self.VS_UDP_PORT)
        self.armed = False
        self.command_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.stream = CameraStream(self.udp_address, **kwargs)
        self.battery = 0
        self.is_flying = False
        self.is_streaming = False

    def help(self):
        print('\n'.join(self.__dict__.keys()))

    def arm(self) -> "DroneController":
        self.armed = True
        self.LOGGER.debug("Binding sockets")
        self.command_socket.bind(self.LOCAL_ADDRESS)
        self.LOGGER.debug("Arming...")
        self._send_command("command")
        # self.get_battery()
        return self

    def streamon(self):
        if self.is_streaming:
            return
        self.is_streaming = True
        self._send_command("streamon")

    def capture_stream(self, show_cam=False):
        if not self.is_streaming:
            self.streamon()
        self.stream.show_video = show_cam
        self.stream.start()

    def streamoff(self):
        if not self.is_streaming:
            return
        self.is_streaming = False
        self._send_command("streamoff")
        self.stream.stop()

    def shutdown(self):
        self.command_socket.close()

    def takeoff(self):
        if self.is_flying:
            return
        self.is_flying = True
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
        try:
            self.battery = int(self._send_command("battery?"))
            return self.battery
        except ValueError:
            return 0

    def get_time(self) -> int:
        return int(self._send_command("time?"))

    def get_height(self) -> int:
        return int(self._send_command("height?"))

    def get_temp(self) -> int:
        return int(self._send_command("temp?"))

    def get_attitude(self) -> IMU:
        return IMU(int(x) for x in self._send_command("attitude?").split())

    def get_barometric(self) -> int:
        return int(self._send_command("baro?"))

    def get_acceleration(self) -> Vec3D:
        return Vec3D(int(x) for x in self._send_command("acceleration?").split())

    def get_tof(self) -> int:
        return self._send_command("tof?")

    def get_wifi(self) -> TelloResponse:
        return TelloResponse.OK if self._send_command("wifi?") == "ok" else TelloResponse.ERROR

    def _send_command(self, cmd: str) -> Any:
        self.LOGGER.debug(cmd)
        self.command_socket.sendto(cmd.encode(encoding="utf-8"), self.TELLO_ADDRESS)
        data = 0
        try:
            data = self.command_socket.recvfrom(1518)[0].decode(encoding="utf-8")
            self.LOGGER.debug(data)
        except Exception as e:
            self.LOGGER.error(e)
        return data

    def end(self):
        self.LOGGER.info("shuting down")
        if self.is_flying:
            self.land()
        if self.is_streaming:
            self.streamoff()

    def __repr__(self):
        return (f"<{self.__class__.__name__}: address={self.udp_address} armed={self.armed} "
                f"flying={self.is_flying} battery={self.battery}>")
