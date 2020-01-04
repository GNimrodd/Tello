import IPython
import argparse
from tello import Tello
from typing import Dict, Callable, Any
from controller import Move, Rotate
from keyboard_controll import KeyboardControl

Frodo = "TELLO-579043"
Sam = "TELLO-578FDA"


def bind_drone(drone: Tello) -> Dict[str, Callable[[Any], Any]]:
    return {'move': Move(drone),
            'rotate': Rotate(drone),
            'takeoff': drone.takeoff,
            'land': drone.land,
            'streamon': drone.streamon,
            'streamoff': drone.streamoff,
            'keyboard': KeyboardControl(drone),
            'drone': drone}


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-ssid", type=str, default=None)
    ap.add_argument("--with-camera", default=False, const=True, nargs='?', help="Set True to see the video stream")
    ap.add_argument("--capture_video", type=str, default=None, help="Pass a file-path for the video")
    ap.add_argument("--keyboard", default=False, const=True, nargs='?', help="Use keyboard keys to control the drone")
    ap.add_argument("--lsd-slam", default=False, const=True, nargs='?', help="Use lsd-slam")
    ap.add_argument("--cam-calibration", type=str, default=None)
    ap.add_argument("--unid-calibration", type=str, default=None)
    args = ap.parse_args()
    if args.lsd_slam:
        if args.cam_calibration is None or args.unid_calibration is None:
            raise ValueError("lsd-slam mode requires cam-calibration and unidistorder calibration files:\n"
                             "main.py --lsd-slam --cam-calibration <path1> --unid-calibration<path2>")
    return args


def main():
    args = get_args()
    drone = Tello(show_video=args.with_camera, ssid=args.ssid)
    drone.connect()
    try:
        drone.streamon()
        if args.lsd_slam:
            raise NotImplemented("lsd-slam mode not yet implemented")  # TODO: remove once implemented
            import lsd_slam
            lsd_slam.run(drone.get_udp_video_address, )
        elif args.capture_video or args.with_camera:
            drone.start_video_cam(save_video=args.capture_video)
        if args.keyboard:
            drone.takeoff()
            KeyboardControl(drone).pass_control()
        else:
            IPython.InteractiveShell.banner2 = (f"DJI Tello drone wifi: {args.ssid}\n "
                                                "Use move, rotate, takeoff or land\n"
                                                "For advanced options, use `drone`\n"
                                                "To finish the run, exit the IPython shell")
            IPython.start_ipython(user_ns=bind_drone(drone))
    finally:
        drone.end()


if __name__ == "__main__":
    main()
