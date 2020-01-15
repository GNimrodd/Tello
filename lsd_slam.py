from utils import generate_logger
import subprocess


class LSDSlamSystem:
    LOGGER = generate_logger("LSDSlamSystem")

    CALIBRATION_FILE = ""
    UNIDISTORTER_FILE = ""
    LSD_SLAM_APP = "lsd_slam/lsd_slam"

    def __init__(self, cam_address):
        self.slam_process = None
        self.cam_address = cam_address

    @property
    def is_initialized(self):
        return self.slam_process is not None

    def start(self):
        process_args = [self.LSD_SLAM_APP, self.cam_address]
        self.LOGGER.debug(f"starting slam procss: {process_args}")
        self.slam_process = subprocess.Popen(process_args, shell=True)

    @property
    def is_alive(self):
        if self.slam_process is not None:
            return self.slam_process.poll() is None

    def terminate(self):
        if self.slam_process is not None:
            self.slam_process.terminate()
