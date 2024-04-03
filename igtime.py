from pygame import time


class Time:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Time, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.clock = time.Clock()

    def tick(self, framerate: int):
        return self.clock.tick(framerate) / 1000
