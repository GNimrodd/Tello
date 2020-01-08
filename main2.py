import IPython
import argparse
from tello2 import DroneController
from typing import Dict, Callable, Any
from keyboard_controll2 import KeyboardControl
import logging
from traitlets.config.loader import Config

DRONES = {"Frodo": "TELLO-579043",
          "Sam": "TELLO-578FDA"}


def set_deinfes(defines) -> Dict[str, Any]:
    defs = {}
    if defines:
        for keyval in defines:
            k, v = keyval.split('=')
            defs[k] = v
    return defs


# python3 main.py --ssid Frodo -v --with-camera --keyboard
def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ssid", type=str)
    ap.add_argument("--verbose", "-v", default=False, const=True, nargs='?', help="run with debug print")
    ap.add_argument("--with-camera", default=False, const=True, nargs='?', help="Set True to see the video stream")
    ap.add_argument("--keyboard", default=False, const=True, nargs='?', help="Use keyboard keys to control the drone")
    ap.add_argument("--lsd-slam", default=False, const=True, nargs='?', help="Use lsd-slam")
    ap.add_argument("--cam-calibration", type=str, default=None)
    ap.add_argument("--unid-calibration", type=str, default=None)
    ap.add_argument("-d", dest='defines', nargs='*')
    args = ap.parse_args()
    if args.lsd_slam:
        if args.cam_calibration is None or args.unid_calibration is None:
            raise ValueError("lsd-slam mode requires cam-calibration and unidistorder calibration files:\n"
                             "main.py --lsd-slam --cam-calibration <path1> --unid-calibration<path2>")
    args.ssid = DRONES.get(args.ssid, args.ssid)
    args.defines = set_deinfes(args.defines)

    return args


def main():
    args = get_args()
    if args.verbose:
        logging.root.setLevel(logging.DEBUG)
    drone = DroneController(ssid=args.ssid, **args.defines)
    drone.arm()
    try:
        if args.with_camera:
            drone.streamon(show_cam=not args.keyboard)
        if args.lsd_slam:
            raise NotImplemented("lsd-slam mode not yet implemented")  # TODO: remove once implemented
            import lsd_slam
            lsd_slam.run(drone.get_udp_video_address, )
        if args.keyboard:
            drone.takeoff()
            KeyboardControl(drone, camera=drone.stream if args.with_camera else None).pass_control()
        else:
            config = Config()
            config.banner2 = (f"DJI Tello drone wifi: {args.ssid}\n "
                              "Use move, rotate, takeoff or land\n"
                              "For advanced options, use `drone`\n"
                              "To finish the run, exit the IPython shell")
            IPython.start_ipython(argv=[], user_ns={'drone': drone}, config=config)
    finally:
        drone.end()


if __name__ == "__main__":
    main()
