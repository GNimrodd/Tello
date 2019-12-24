import IPython
import argparse
from tello import Tello
from typing import Dict, Callable, Any
from controller import Move, Rotate
import wifi


def connect_wifi(ssid: str):
    wifi.Scheme.find('wlan0', ssid).activate()


Frodo = "TELLO-579043"
Sam = "TELLO-578FDA"


def bind_drone(drone: Tello) -> Dict[str, Callable[[Any], Any]]:
    return {'move': Move(drone),
            'rotate': Rotate(drone),
            'takeoff': drone.takeoff,
            'land': drone.land,
            'streamon': drone.streamon,
            'streamoff': drone.streamoff,
            'drone': drone}


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-wifi", default=None)
    ap.add_argument("--with-camera", default=False, const=True, nargs='?', help="set True to see the video stream")
    ap.add_argument("--capture_video", type=str, default=None, help="pass a file-path for the video")
    return ap.parse_args()


def main():
    args = get_args()
    if args.wifi:
        connect_wifi(args.wifi)
    drone = Tello(show_video=args.with_camera)
    drone.connect()
    if args.with_camera:
        drone.streamon()
        drone.start_video_cam(save_video=args.capture_video)

    IPython.InteractiveShell.banner2 = (f"DJI Tello drone wifi: {args.wifi}\n "
                                        "Use move, rotate, takeoff or land\n"
                                        "For advanced options, use `drone`")
    IPython.start_ipython(user_ns=bind_drone(drone))
    if drone.is_flying:
        drone.land()


if __name__ == "__main__":
    main()
