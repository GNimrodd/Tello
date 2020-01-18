from utils import generate_logger
import subprocess
import signal


class LSDSlamSystem:
    LOGGER = generate_logger("LSDSlamSystem")

    CALIBRATION_FILE = "/home/nimrodd/code/Tello/lsd_slam/calib.xml"
    UNIDISTORTER_FILE = "/home/nimrodd/code/Tello/lsd_slam/calib.xml"
    LSD_SLAM_APP = "/home/nimrodd/code/lsd_slam_noros/bin/sample_app"

    def __init__(self, cam_address):
        self.slam_process = None
        self.cam_address = cam_address

    @property
    def is_initialized(self):
        return self.slam_process is not None

    def start(self):
        signal.signal(signal.SIGINT, self.__on_sigkill)
        process_args = [self.LSD_SLAM_APP, self.cam_address, self.CALIBRATION_FILE, self.UNIDISTORTER_FILE]
        self.LOGGER.debug(f"starting slam process: {' '.join(process_args)}")
        self.slam_process = subprocess.Popen(process_args, shell=False)
        self.LOGGER.debug(f"slam process pid: {self.slam_process.pid}")

    @property
    def is_alive(self):
        if self.slam_process is not None:
            return self.slam_process.poll() is None

    def terminate(self):
        if self.slam_process is not None:
            self.slam_process.terminate()

    def __on_sigkill(self, signum, frame):
        self.terminate()
        exit(0)


if __name__ == "__main__":
    import logging
    LSDSlamSystem.LOGGER.setLevel(logging.DEBUG)
    slam_system = LSDSlamSystem("0")
    slam_system.start()
