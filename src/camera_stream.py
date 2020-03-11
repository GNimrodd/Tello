import cv2
from threading import Thread
from typing import Optional
from datetime import datetime
import time
import os
from utils import logger_mixin, RUN_ID


class CameraStream(logger_mixin()):
"""
    Camera stream controller.
"""
    def __init__(self, device: Optional[str] = None, **kwargs):
        self.device = device  # the address of the drone cam
        self.show_cam = kwargs.get('show_cam', False)  # display a the video stream in a window
        self.video_capture = cv2.VideoCapture(device) if device else None
        self.capture_frames = kwargs.get('capture_frames', False)  # flag: save the captured frames
        self.capture_frame_dir = kwargs.get('frame_dir', 'frames')  # path to dir where frames are saved
        self.capture_rate = float(kwargs.get('frame_capture_rate', 0.1))  # capture every `capture_rate` seconds
        self.running = False
        self.grabbed = None
        self.frame = None
        self.thread = Thread(target=self.update_frame, args=())

    def set_video_capture(self, device: str):
        if self.device:
            raise ValueError("device already open")
        self.device = device
        self.video_capture = cv2.VideoCapture(device)

    def _open(self):
        if self.video_capture is None:
            raise ValueError("unknown device")
        if not self.video_capture.isOpened():
            self.video_capture.open(self.device)

    def start(self):
        if self.running:
            return self
        self.running = True
        self._open()
        self.grabbed, self.frame = self.video_capture.read()
        self.thread.start()
        return self

    def get_frames(self):
        return self.grabbed, self.frame

    def update_frame(self):
        try:
            with open(f"{self.capture_frame_dir}/frame_list_{RUN_ID}.txt", 'w') as frame_data_file:
                previous_time = time.time()
                need_capture = True
                while self.running:
                    current_time = time.time()
                    if current_time > previous_time + self.capture_rate:
                        previous_time = current_time
                        need_capture = True
                    if not self.grabbed or not self.video_capture.isOpened():
                        self.stop()
                    else:
                        self.grabbed, self.frame = self.video_capture.read()
                    if self.capture_frames and need_capture:
                        need_capture = False
                        file_name = self.snapshot(f"{self.capture_frame_dir}/{int(current_time * 1000)}.jpeg")
                        frame_data_file.write(f"{current_time} {os.path.abspath(file_name)}\n")
                    if self.show_video:
                        cv2.imshow('tello-cam', self.frame)
                        if not self.running or cv2.waitKey(1) & 0xFF == ord('q'):
                            self.stop()
                            cv2.destroyAllWindows()
        finally:
            if self.show_video:
                cv2.destroyAllWindows()

    def snapshot(self, path: Optional[str] = None) -> str:
        img_path = path or datetime.now().strftime('%Y%m%d-%H%M%S') + ".jpeg"
        cv2.imwrite(img_path, self.frame)
        return img_path

    def stop(self):
        if self.running:
            self.running = False
            self.thread.join()
