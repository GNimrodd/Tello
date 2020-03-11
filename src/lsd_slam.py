from utils import logger_mixin, CommandLineParser, GLOBALS, update_global
import subprocess
import signal
from typing import Union

LIVE = 0
OFFLINE = 1

"""
The files are hardcoded and should be replaced here:
"""

CALIBRATION_FILE = "/home/nimrodd/code/Tello/lsd_slam/calibration.xml"
LSD_SLAM_LIVE_APP = "/home/nimrodd/code/lsd_slam_noros/bin/live_main"
LSD_SLAM_OFFLINE_APP = "/home/nimrodd/code/lsd_slam_noros/bin/main_on_images"


def get_lsd_slam_app(app_type: Union[str, int]) -> str:
    if app_type in (LIVE, "live"):
        return GLOBALS["lsd_slam_live_app"]
    elif app_type in (OFFLINE, "offline"):
        return GLOBALS["lsd_slam_offline_app"]
    else:
        raise ValueError(f"Unknown app type: {app_type}")


class LSDSlamSystem(logger_mixin()):
    update_global('lsd_slam_live_app', "/home/nimrodd/code/lsd_slam_noros/bin/live_main", False)
    update_global('lsd_slam_offline_app', "/home/nimrodd/code/lsd_slam_noros/bin/main_on_images", False)

    def __init__(self, input_source, app_type: Union[str, int] = LIVE, calibration_file: str = CALIBRATION_FILE):
        self.slam_process = None
        self.input_source = input_source
        self.application = get_lsd_slam_app(app_type)
        self.calibration_file = calibration_file

    @property
    def is_initialized(self):
        return self.slam_process is not None

    def start(self) -> "LSDSlamSystem":
        signal.signal(signal.SIGINT, self.__on_sigint)
        process_args = [self.app, self.input_source, self.calibration_file]
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


class Main(CommandLineParser):
    def __init__(self):
        super().__init__(prog="LSD-SLAM Wrapper")
        self.add_argument('run_type', type=str, choices=['offline', 'live'])
        self.add_argument('--calibration', type=str)
        self.add_argument('-input', type=str)
        args = self.parse_args()
        self.run_type = LIVE if args.live else OFFLINE
        self.input_source = args.input
        self.slam_system = LSDSlamSystem(self.input_source, self.run_type, self.args.calibration)

    def main(self):
        self.slam_system.start().wait_on_slam()


if __name__ == "__main__":
    Main().main()
