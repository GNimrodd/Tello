import cv2
from threading import Thread
from typing import Optional
from datetime import datetime


class CameraStream:

    def __init__(self, udp_address: str):
        self.show_video = False
        self.udp_address = udp_address
        self.video_capture = cv2.VideoCapture(udp_address)
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
            while self.running:
                if not self.grabbed or not self.video_capture.isOpened():
                    self.stop()
                else:
                    self.grabbed, self.frame = self.video_capture.read()
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
        self.running = False
        self.thread.join()