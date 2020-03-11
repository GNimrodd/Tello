import argparse
from tello import DroneController
from keyboard_controller import KeyboardControl
from utils import CommandLineParser, GLOBALS
from lsd_slam import LSDSlamSystem
import time



"""
    The TELLO drones have a unique wifi, each named TELLO-XXXXX, We've hardcoded our drones here. Change this so it 
    fits yours. 
"""
DRONES = {"Frodo": "TELLO-579043",
          "Sam": "TELLO-578FDA"}

class Main(CommandLineParser):
    """
        command-line terminal for the project.
        --ssid  :   The drone to be controlled. It should be active and searching for connection to work.

        --doa-check :   Quick check for connectivity and battery.
        --with-camera   :   Set True to recieve video stream from drone.
        --keyboard  :   Use the keyboard to control the drone. Press 'H' afterwards to receive instructions
        --lsd-slam  :   Activate LSD-SLAM for the drone, overrides camera.
        capture_frames  :   save the captured frames from the camera
        frame_dir   :   The dir where the frames are saved
        frame_capture_rate  : rate of capture, default is 0.1

        Example:
        python3 main.py --ssid Frodo --keyboard --with-camera --verbose -d capture_frame frame_dir=frames frame_capture_rate=0.2
    """
    
    def __init__(self):
        super().__init__(prog="DJI Tello LSD-SLAM")
        self.add_argument("--ssid", type=str, required=True)
        self.add_argument("--doa-check", default=False, const=True, nargs="?",
                        help="connect to drone, get battery and exit")
        self.add_argument("--with-camera", default=False, const=True, nargs='?', help="Set True to see the video stream")
        self.add_argument("--keyboard", default=False, const=True, nargs='?',
                        help="Use keyboard keys to control the drone")
        self.add_argument("--lsd-slam", default=False, const=True, nargs='?', help="Use lsd-slam")
        self.parse_args()
       
        self.args.ssid = DRONES.get(self.args.ssid, self.args.ssid)
        if self.args.run_doa:
            self.set_debug()

        self.drone = None
        self.slam_system = None

    def _post_init(self):
        self.drone = DroneController(ssid=self.args.ssid, **GLOBALS)
        self.drone.arm()
        self.slam_system = LSDSlamSystem(self.drone.udp_address, **GLOBALS)

    def run_doa(self):
        try:
            self.logger.info(f"running dead-or-alive checks for {self.args.ssid}")
            self.drone.arm()
            self.logger.info(self.drone.get_battery())
            if self.args.lsd_slam:
                self.logger.info("testing slam system")
                self.logger.info("Initializing drone stream")
                self.drone.streamon()
                self.logger.info("initializing slam process")
                self.slam_system.start()
                self.logger.info("sleeping for 1 minute...")
                time.sleep(60)
            else:
                self.logger.info("taking snapshot")
                self.drone.capture_stream(False)
                self.drone.stream.snapshot()
        except Exception:
            self.logger.error("dead-or-alive failed")
            raise
        self.logger.info("dead-or-alive passed")

    def main(self):
        self._post_init()
        try:
            self.run_doa() if self.args.run_doa else self.run()
        finally:
            self.slam_system.terminate()
            self.drone.end()

    def run(self):
        show_video = self.args.with_camera and not self.args.lsd_slam
        if show_video:
            self.drone.capture_stream(show_cam=False)
        if self.args.lsd_slam:
            self.drone.streamon()
            self.slam_system.start()
        KeyboardControl(self.drone, camera=self.drone.stream if show_video else None).pass_control(
            (lambda: not self.slam_system.is_alive()) if self.slam_system.is_initialized else (lambda: False))


if __name__ == "__main__":
    try:
        Main().main()
    except (argparse.ArgumentError, argparse.ArgumentTypeError) as e:
        print(e)
    except Exception as e:
        print(f"Unexpected exception: {e}")
