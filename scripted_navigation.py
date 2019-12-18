from .controller import Tello


class ScriptedMovement:
    def __init__(self, drone: Tello):
        self.drone = drone

    def execute(self, *args, **kwargs):
        raise NotImplemented()


class CircleAround(ScriptedMovement):
    def __init__(self, drone: Tello, radius: int):
        super().__init__(drone)
        self.radius = radius

    def execute(self, *args, **kwargs):
        pass



