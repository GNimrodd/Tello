from threading import Thread
import cv2
import socket
import time


class CameraStream(Thread):
    '''
    Inspired by:
    https://github.com/damiafuentes/DJITelloPy/tree/73405c2652fce4c02264c489146605596a2216f4
    '''
    VS_UDP_IP = '0.0.0.0'
    VS_UDP_PORT = 11111

    def __init__(self, name: str = "Video"):
        super().__init__()
        self.name = name
        self.cap = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.grabbed, self.frame = None, None
        self.stopped = False
        self.outfile = f"{name}_{int(time.time())}.h264"
        # self.writer = cv2.VideoWriter(self.outfile)

    @property
    def udp_video_address(self):
        return f"udp://@{self.VS_UDP_IP}:{str(self.VS_UDP_PORT)}"

    def _update_frame(self):
        while not self.stopped:
            if not self.grabbed or not self.cap.isOpened():
                self.stop()
            else:
                (self.grabbed, self.frame) = self.cap.read()
            # self.writer.write(self.frame)
            cv2.imshow(self.name, self.frame)
            if self.stopped or cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop()
                cv2.destroyAllWindows()

    def stop(self):
        self.stopped = True

    def run(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.udp_video_address)
        if not self.cap.isOpened():
            self.cap.open(self.udp_video_address)
        self.grabbed, self.frame = self.cap.read()
        self._update_frame()
