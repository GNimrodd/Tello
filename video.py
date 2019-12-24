import cv2
from threading import Thread


class BackgroundFrameRead:
    """
    This class read frames from a VideoCapture in background. Then, just call backgroundFrameRead.frame to get the
    actual one.
    """

    def __init__(self, tello, address, show_video: bool = True, name: str = "", **kwargs):
        self.show_video = show_video
        self.name = name
        tello.cap = cv2.VideoCapture(address)
        self.cap = tello.cap
        save_video = kwargs.get('save_video', None)
        self.video_writer = cv2.VideoWriter(save_video, 'H264') if save_video else None

        if not self.cap.isOpened():
            self.cap.open(address)

        self.grabbed, self.frame = self.cap.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update_frame, args=()).start()
        return self

    def update_frame(self):
        try:
            while not self.stopped:
                if not self.grabbed or not self.cap.isOpened():
                    self.stop()
                else:
                    (self.grabbed, self.frame) = self.cap.read()
                if self.show_video:
                    cv2.imshow(self.name, self.frame)
                    if self.video_writer:
                        self.video_writer.write(self.frame)
                    if self.stopped or cv2.waitKey(1) & 0xFF == ord('q'):
                        self.stop()
                        cv2.destroyAllWindows()
        finally:
            cv2.destroyAllWindows()

    def stop(self):
        self.stopped = True
