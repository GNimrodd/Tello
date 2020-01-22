import cv2
from threading import Thread
from typing import Optional
from datetime import datetime
import time


class CameraStream:

    def __init__(self, udp_address: str, **kwargs):
        self.show_video = False  # display a the video stream in a window
        self.udp_address = udp_address  # the address of the drone cam
        self.video_capture = cv2.VideoCapture(udp_address)
        self.capture_frames = kwargs.get('capture_frames', False)  # flag: save the captured frames
        self.capture_frame_dir = kwargs.get('frame_dir', 'frames')  # path to dir where frames are saved
        self.capture_rate = kwargs.get('frame_capture_rate', 0.2) * 1000  # capture every `capture_rate` seconds
        self.frame_data_file = open(f"{self.capture_frame_dir}/frame_data.txt", 'w') if self.capture_frames else None
        self.running = False
        self.grabbed = None
        self.frame = None
        self.thread = Thread(target=self.update_frame, args=())

    def _open(self):
        if not self.video_capture.isOpened():
            self.video_capture.open(self.udp_address)

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
            previous_time = time.time()
            capture = True
            while self.running:
                current_time = time.time()
                if current_time > previous_time + 3000:
                    previous_time = current_time
                    capture = True
                if not self.grabbed or not self.video_capture.isOpened():
                    self.stop()
                else:
                    self.grabbed, self.frame = self.video_capture.read()
                if self.capture_frames and capture:
                    capture = False
                    file_name = self.snapshot(f"{self.capture_frame_dir}/{int(current_time)}.jpeg")
                    self.frame_data_file.write(f"tag {current_time} {file_name}")
                if self.show_video:
                    cv2.imshow('tello-cam', self.frame)
                    if not self.running or cv2.waitKey(1) & 0xFF == ord('q'):
                        self.stop()
                        cv2.destroyAllWindows()
        finally:
            if self.show_video:
                cv2.destroyAllWindows()
            if self.frame_data_file:
                self.frame_data_file.close()

    def snapshot(self, path: Optional[str] = None) -> str:
        img_path = path or datetime.now().strftime('%Y%m%d-%H%M%S') + ".jpeg"
        cv2.imwrite(img_path, self.frame)
        return img_path

    def stop(self):
        if self.running:
            self.running = False
            self.thread.join()
