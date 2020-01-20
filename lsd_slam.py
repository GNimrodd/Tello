from utils import generate_logger
import subprocess
import signal


LIVE = 0
OFFLINE = 1


class LSDSlamSystem:
    LOGGER = generate_logger("LSDSlamSystem")

    CALIBRATION_FILE = "/home/nimrodd/code/Tello/lsd_slam/calib.xml"
    UNIDISTORTER_FILE = "/home/nimrodd/code/Tello/lsd_slam/calib.xml"
    LSD_SLAM_LIVE_APP = "/home/nimrodd/code/lsd_slam_noros/bin/sample_app"
    LSD_SLAM_OFFLINE_APP = "/home/nimrodd/code/lsd_slam_noros/bin/main_on_images"

    LSD_SLAM_APPS = {LIVE: LSD_SLAM_LIVE_APP, OFFLINE: LSD_SLAM_OFFLINE_APP}

    def __init__(self, cam_address, app=LIVE):
        if app not in (LIVE, OFFLINE):
            raise ValueError("app must be <lsd_slam.LIVE/lsd_slam.OFFLINE>")
        self.slam_process = None
        self.cam_address = cam_address
        self.app = self.LSD_SLAM_APPS[app]

    @property
    def is_initialized(self):
        return self.slam_process is not None

    def start(self) -> "LSDSlamSystem":
        signal.signal(signal.SIGINT, self.__on_sigint)
        process_args = [self.app, self.cam_address, self.CALIBRATION_FILE, self.UNIDISTORTER_FILE]
        self.LOGGER.debug(f"starting slam process: {' '.join(process_args)}")
        self.slam_process = subprocess.Popen(process_args, shell=False)
        self.LOGGER.debug(f"slam process pid: {self.slam_process.pid}")
        return self

    @property
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


if __name__ == "__main__":
    import logging
    LSDSlamSystem.LOGGER.setLevel(logging.DEBUG)
    slam_system = LSDSlamSystem("0")
    slam_system.start().wait_on_slam()
