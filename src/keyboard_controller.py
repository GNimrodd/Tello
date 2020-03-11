import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
from tello import DroneController
from typing import Tuple, Callable
import cv2
from utils import logger_mixin
from camera_stream import CameraStream


class KeyboardControl(logger_mixin()):
    """
    controlling the drone via keyboard, will display the camera information if set to work.
    """

    def __init__(self, drone: DroneController, control_window_size: Tuple[int, int] = (1280, 720),
                 camera: CameraStream = None):
        self.drone = drone
        self.move_amount = 50
        self.rotate_amount = 45
        self.camera = camera
        self.control_window_size = control_window_size
        self.screen = None

    def __repr__(self):
        return f"<{self.__class__.__name__} for {self.drone}>"

    def pass_control(self, exit_check: Callable[[], bool] = lambda: False):
        self.logger.debug("Passing control to keyboard, press 'h' for help")
        pygame.init()
        self.screen = pygame.display.set_mode(self.control_window_size)
        pygame.display.set_caption("DJI Tello Control Window")
        running = True
        while running:

            if exit_check():
                self.logger.debug("lsd-slam process died, exiting...")
                running = False

            if self.camera is not None:
                ret, frame = self.camera.get_frames()
                if frame is not None:
                    self.screen.fill([0, 0, 0])
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = frame.swapaxes(0, 1)
                    frame = pygame.surfarray.make_surface(frame)
                    self.screen.blit(frame, (0, 0))
                    pygame.display.update()
                else:
                    self.logger.error("Couldn't get frame to display")

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.K_t:
                        self.drone.takeoff()
                        self.logger.debug("taking off")
                    if event.key == pygame.K_RIGHT:
                        self.drone.move.right(self.move_amount)
                        self.logger.debug(f"moving {self.move_amount} to the right")
                    elif event.key == pygame.K_LEFT:
                        self.drone.move.left(self.move_amount)
                        self.logger.debug(f"moving {self.move_amount} to the left")
                    elif event.key == pygame.K_UP:
                        self.drone.move.forward(self.move_amount)
                        self.logger.debug(f"moving {self.move_amount} forwards")
                    elif event.key == pygame.K_DOWN:
                        self.drone.move.back(self.move_amount)
                        self.logger.debug(f"moving {self.move_amount} backwards")
                    elif event.key == pygame.K_q:
                        self.drone.rotate.ccw(self.rotate_amount)
                        self.logger.debug(f"rotating {self.rotate_amount} counter-clockwise")
                    elif event.key == pygame.K_e:
                        self.drone.rotate.cw(self.rotate_amount)
                        self.logger.debug(f"rotating {self.rotate_amount} clockwise")
                    elif event.key == pygame.K_s:
                        self.drone.move.down(self.move_amount)
                        self.logger.debug(f"moving {self.move_amount} down")
                    elif event.key == pygame.K_w:
                        self.drone.move.up(self.move_amount)
                        self.logger.debug(f"moving {self.move_amount} up")
                    elif event.key == pygame.K_ESCAPE:
                        self.logger.debug("Returning control")
                        self.drone.end()
                        running = False
                    elif event.key == pygame.K_p:
                        img_path = self.camera.snapshot()
                        self.logger.debug(f"printscreen: {img_path}")
                    elif event.key == pygame.K_h:
                        print(
                            "Drone is being controlled by keyboard;\n"
                            "\t- Arrow Up:      move forward\n"
                            "\t- Arrow Down:    move backward\n"
                            "\t- Arrow Left:    move left\n"
                            "\t- Arrow Right:   move right\n"
                            "\t- s:             move down\n"
                            "\t- w:             move up\n"
                            "\t- q:             rotate counter clockwise\n"
                            "\t- e:             rotate clockwise\n"
                            "\t- t:             take off"
                        )

        pygame.quit()
        cv2.destroyAllWindows()