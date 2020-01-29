from utils import generate_logger
import subprocess
import signal
import argparse
import logging
import sys
import os

LIVE = 0
OFFLINE = 1
CALIBRATION_FILE = "/home/nimrodd/code/Tello/lsd_slam/calibration.xml"
UNIDISTORTER_FILE = "/home/nimrodd/code/Tello/lsd_slam/calibration.xml"
# LSD_SLAM_LIVE_APP = "/home/nimrodd/code/lsd_slam_noros/bin/sample_app"
LSD_SLAM_LIVE_APP = "/home/nimrodd/code/lsd_slam_noros/bin/live_main"
LSD_SLAM_OFFLINE_APP = "/home/nimrodd/code/lsd_slam_noros/bin/main_on_images"


class LSDSlamSystem:
    LOGGER = generate_logger("LSDSlamSystem")

    LSD_SLAM_APPS = {LIVE: LSD_SLAM_LIVE_APP, OFFLINE: LSD_SLAM_OFFLINE_APP}

    def __init__(self, input_source, app=LIVE, calibration_file: str = CALIBRATION_FILE):
        if app not in (LIVE, OFFLINE):
            raise ValueError("app must be <lsd_slam.LIVE/lsd_slam.OFFLINE>")
        self.slam_process = None
        self.input_source = input_source
        self.app = self.LSD_SLAM_APPS[app]
        self.calibration_file = calibration_file

    @property
    def is_initialized(self):
        return self.slam_process is not None

    def start(self) -> "LSDSlamSystem":
        signal.signal(signal.SIGINT, self.__on_sigint)
        process_args = [self.app, self.input_source, self.calibration_file, UNIDISTORTER_FILE]
        self.LOGGER.debug(f"starting slam process: {' '.join(process_args)}")
        self.slam_process = subprocess.Popen(process_args, shell=False)
        self.LOGGER.debug(f"slam process pid: {self.slam_process.pid}")
        return self

    def is_alive(self):
        if self.slam_process is not None:
            return self.slam_process.poll() is None

    def terminate(self):
        if self.slam_process is not None:
            self.slam_process.terminate()

    def wait_on_slam(self):
        if self.slam_process:
            self.slam_process.wait()
        else:
            raise ValueError("slam process isn't running, can't wait on it")

    def __on_sigint(self, signum, frame):
        self.terminate()
        exit(0)

    def __del__(self):
        self.terminate()


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('-live', default=False, const=True, nargs='?')
    ap.add_argument('-offline', default=False, const=True, nargs='?')
    ap.add_argument('--calibration', type=str)
    ap.add_argument('-cam', default='')
    ap.add_argument('-frames', default='')
    ap.add_argument('--verbose', '-v', default=False, const=Tue, nargs='?')
    args = ap.parse_args()
    if not args.live ^ args.offline:
        raise argparse.ArgumentError("must use one of <live/offline>")
    if args.live and not args.cam:
        raise argparse.ArgumentError("live slam requires a cam")
    if args.offline and not args.frames:
        raise argparse.ArgumentError("offline slam requires a frame file")
    args.run_type = LIVE if args.live else OFFLINE
    args.input = args.cam if args.live else args.frames
    return args


if __name__ == "__main__":
    args = get_args()
    if args.verbose:
        LSDSlamSystem.LOGGER.setLevel(logging.DEBUG)
    slam_system = LSDSlamSystem(args.input, args.run_type, args.calibration)
    slam_system.start().wait_on_slam()
