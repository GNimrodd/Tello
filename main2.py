import IPython
import argparse
from tello2 import DroneController
from typing import Dict, Callable, Any
from keyboard_controll2 import KeyboardControl
import logging
from traitlets.config.loader import Config
import subprocess
from utils import generate_logger, set_all_loggers
from lsd_slam import LSDSlamSystem

DRONES = {"Frodo": "TELLO-579043",
          "Sam": "TELLO-578FDA"}


def set_deinfes(defines) -> Dict[str, Any]:
    defs = {}
    if defines:
        for keyval in defines:
            kv = keyval.split('=')
            if len(kv) == 1:
                defs[kv] = True
            elif len(kv) == 2:
                defs[kv[0]] = kv[1]
            else:
                raise argparse.ArgumentError("defines can contain only one =")
    return defs


# python3 main.py --ssid Frodo -v --with-camera --keyboard
def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ssid", type=str)
    ap.add_argument("--doa-check", default=False, const=True, nargs="?", help="connect to drone, get battery and exit")
    ap.add_argument("--verbose", "-v", default=False, const=True, nargs='?', help="run with debug print")
    ap.add_argument("--with-camera", default=False, const=True, nargs='?', help="Set True to see the video stream")
    ap.add_argument("--keyboard", default=False, const=True, nargs='?', help="Use keyboard keys to control the drone")
    ap.add_argument("--lsd-slam", default=False, const=True, nargs='?', help="Use lsd-slam")
    ap.add_argument("--slam-exe", default=None, type=str, help="path of slam executable")
    # ap.add_argument("--cam-calibration", type=str, default=None)
    # ap.add_argument("--unid-calibration", type=str, default=None)
    ap.add_argument("-d", dest='defines', nargs='*')
    args = ap.parse_args()
    # if args.lsd_slam:
    #     if args.cam_calibration is None or args.unid_calibration is None:
    #         raise ValueError("lsd-slam mode requires cam-calibration and unidistorder calibration files:\n"
    #                          "main.py --lsd-slam --cam-calibration <path1> --unid-calibration<path2>")
    args.ssid = DRONES.get(args.ssid, args.ssid)
    if args.doa_check:
        args.verbose = True
    args.defines = set_deinfes(args.defines)

    return args


def set_logger_to_debug():
    set_all_loggers(lambda l: l.setLevel(logging.DEBUG))


class Main:
    LOGGER = generate_logger('main')

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.drone = None
        self.slam_system = None
        if args.verbose:
            set_logger_to_debug()
        if args.slam_exe:
            LSDSlamSystem.LSD_SLAM_LIVE_APP = args.slam_exe

    def _post_init(self):
        self.drone = DroneController(ssid=self.args.ssid, **self.args.defines)
        self.drone.arm()
        self.slam_system = LSDSlamSystem(self.drone.udp_address)

    def run_doa(self):
        try:
            self.LOGGER.info(f"running dead-or-alive checks for {self.args.ssid}")
            self.drone.arm()
            self.LOGGER.info(self.drone.get_battery())
            if self.args.lsd_slam:
                self.LOGGER.info("testing slam system")
                self.LOGGER.info("Initializing drone stream")
                self.drone.streamon()
                self.LOGGER.info("initializing slam process")
                self.slam_system.start()
                self.LOGGER.info("sleeping for 1 minute...")
                import time
                time.sleep(60)
            else:
                self.LOGGER.info("taking snapshot")
                self.drone.capture_stream(False)
                self.drone.stream.snapshot()
        except Exception:
            self.LOGGER.error("dead-or-alive failed")
            raise
        self.LOGGER.info("dead-or-alive passed")

    def main(self):
        self._post_init()
        try:
            self.run_doa() if self.args.doa_check else self.run()
        finally:
            self.slam_system.terminate()
            self.drone.end()

    def run(self):
        # battery = self.drone.get_battery()
        # if battery < 20:
        #     raise ValueError(f"low battery: {battery}")
        if self.args.with_camera and not self.args.lsd_slam:
            self.drone.capture_stream(show_cam=not self.args.keyboard)
        if self.args.lsd_slam:
            self.drone.streamon()
            self.slam_system.start()
        if self.args.keyboard:
            # KeyboardControl(self.drone, camera=self.drone.stream if self.args.with_camera else None).pass_control(
            #     (lambda: self.slam_system.is_alive()) if self.slam_system.is_initialized else (lambda: False))
            KeyboardControl(self.drone, camera=self.drone.stream if self.args.with_camera else None).pass_control(
                lambda: False)
        else:
            config = Config()
            config.banner2 = (f"DJI Tello drone wifi: {self.args.ssid}\n "
                              "Use move, rotate, takeoff or land\n"
                              "For advanced options, use `drone`\n"
                              "To finish the run, exit the IPython shell")
            IPython.start_ipython(argv=[], user_ns={'drone': self.drone}, config=config)


# python3 main2.py --ssid Frodo --keyboard --show-cam --verbose -d capture_frame -d frame_dir=frames -d frame_capture_rate=0.2


if __name__ == "__main__":
    try:
        Main(get_args()).main()
    except (argparse.ArgumentError, argparse.ArgumentTypeError) as e:
        print(e)
    except Exception as e:
        print(f"Unexpected exception: {e}")
