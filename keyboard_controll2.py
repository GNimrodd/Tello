import pygame
from tello2 import DroneController
from typing import Tuple
import logging
import cv2
import numpy as np
from utils import generate_logger
from camera_stream import CameraStream
from datetime import datetime


class MockCam:
    def __init__(self):
        self.cap = cv2.VideoCapture(-1)
        self.ret, self.frame = None, None
        if not self.cap.isOpened():
            self.cap.open(-1)

    def get_frames(self):
        self.ret, self.frame = self.cap.read()
        return self.ret, self.frame

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class KeyboardControl:
    """
    controlling the drone via keyboard
    """

    LOGGER = generate_logger("KeyboardController")

    def __init__(self, drone: DroneController, control_window_size: Tuple[int, int] = (1280, 720),
                 camera: CameraStream = None):
        self.drone = drone
        self.move_amount = 20
        self.rotate_amount = 30
        self.camera = camera
        self.control_window_size = control_window_size
        self.screen = None

    def __repr__(self):
        return f"<{self.__class__.__name__} for {self.drone}>"

    def pass_control(self):
        self.LOGGER.debug("Passing control to keyboard, press 'h' for help")
        pygame.init()
        self.screen = pygame.display.set_mode(self.control_window_size)
        pygame.display.set_caption("DJI Tello Control Window")
        running = True
        while running:
            if self.camera is not None:
                ret, frame = self.camera.get_frames()
                self.screen.fill([0, 0, 0])
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = frame.swapaxes(0, 1)
                frame = pygame.surfarray.make_surface(frame)
                self.screen.blit(frame, (0, 0))
                pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.drone.move.right(self.move_amount)
                        self.LOGGER.debug(f"moving {self.move_amount} to the right")
                    elif event.key == pygame.K_LEFT:
                        self.drone.move.left(self.move_amount)
                        self.LOGGER.debug(f"moving {self.move_amount} to the left")
                    elif event.key == pygame.K_UP:
                        self.drone.move.forward(self.move_amount)
                        self.LOGGER.debug(f"moving {self.move_amount} forwards")
                    elif event.key == pygame.K_DOWN:
                        self.drone.move.back(self.move_amount)
                        self.LOGGER.debug(f"moving {self.move_amount} backwards")
                    elif event.key == pygame.K_q:
                        self.drone.rotate.ccw(self.rotate_amount)
                        self.LOGGER.debug(f"rotating {self.rotate_amount} counter-clockwise")
                    elif event.key == pygame.K_e:
                        self.drone.rotate.cw(self.rotate_amount)
                        self.LOGGER.debug(f"rotating {self.rotate_amount} clockwise")
                    elif event.key == pygame.K_LCTRL:
                        self.drone.move.down(self.move_amount)
                        self.LOGGER.debug(f"moving {self.move_amount} down")
                    elif event.key == pygame.K_LALT:
                        self.drone.move.up(self.move_amount)
                        self.LOGGER.debug(f"moving {self.move_amount} up")
                    elif event.key == pygame.K_ESCAPE:
                        self.LOGGER.debug("Returning control")
                        self.drone.end()
                        running = False
                    elif event.key == pygame.K_p:
                        img_path = datetime.now().strftime('%Y%m%d-%H%M%S') + ".jpeg"
                        self.LOGGER.debug(f"printscreen: {img_path}")
                        cv2.imwrite(img_path, self.camera.frame)
                    elif event.key == pygame.K_h:
                        print(
                            "Drone is being controlled by keyboard;\n"
                            "\t- Arrow Up:      move forward\n"
                            "\t- Arrow Down:    move forward\n"
                            "\t- Arrow Left:    move forward\n"
                            "\t- Arrow Right:   move forward\n"
                            "\t- Left Ctrl:     move forward\n"
                            "\t- Left Alt:      move forward\n"
                            "\t- q:             rotate counter clockwise\n"
                            "\t- e:             rotate clockwise\n"
                        )
        pygame.quit()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    from mock import MagicMock

    drone = MagicMock()
    kc = KeyboardControl(drone, camera=MockCam())
    KeyboardControl.LOGGER.setLevel(logging.DEBUG)
    kc.pass_control()
