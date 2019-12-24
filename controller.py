from tello import Tello


class Controller:
    def __init__(self, drone: Tello):
        self.drone = drone

    def __repr__(self):
        return f"<{self.__class__.__name__}>"


class Move(Controller):
    def __init__(self, drone: Tello):
        super().__init__(drone)

    def up(self, x: int):
        self.drone.move_up(x)

    def down(self, x: int):
        self.drone.move_down(x)

    def left(self, x: int):
        self.drone.move_left(x)

    def right(self, x: int):
        self.drone.move_right(x)

    def forward(self, x: int):
        self.drone.move_forward(x)

    def back(self, x: int):
        self.drone.move_back(x)


class Rotate(Controller):
    def __init__(self, drone: Tello):
        super().__init__(drone)

    def cw(self, x: int):
        self.drone.rotate_clockwise(x)

    def ccw(self, x: int):
        self.drone.rotate_counter_clockwise(x)
