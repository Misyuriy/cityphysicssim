from copy import deepcopy
import random

import graphics
from graphics import Window, InputType, Color
import physics
from physics import Vector2, Point2, Object

import city
from city import Building

import igtime

import settings
import maps


class Camera:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Camera, cls).__new__(cls)
        return cls.instance

    def __init__(self,
                 position: tuple | list | Point2 | Vector2 = Vector2(0, 0),
                 shape: tuple | list | Point2 | Vector2 = Vector2(0, 0)):
        self.position: Vector2 = Vector2(*position)

        self.shape: Vector2 = Vector2(*shape)

    def get_center_position(self):
        return self.position + (0.5 * Vector2(self.shape))

    def get_relative_position(self, global_position: Vector2):
        return global_position - self.position

    def get_global_position(self, relative_position: Vector2):
        return relative_position + self.position


def mainloop():
    window = Window([600, 600], 'Пригожин женя')
    camera = Camera(shape=[600, 600])
    time = igtime.Time()

    running = True
    objects: list[Object] = [] #maps.test_map.get_objects()

    while running:
        #objects[0].rotation += 0.5
        for event in window.get_input():
            match event:
                case InputType.W:
                    camera.position.y -= 2
                case InputType.A:
                    camera.position.x -= 2
                case InputType.S:
                    camera.position.y += 2
                case InputType.D:
                    camera.position.x += 2

                case InputType.QUIT:
                    running = False

        window.clear()
        for obj in objects:
            obj.render_to(window, camera)

            for obj2 in objects:
                if obj != obj2 and obj.is_colliding_with(obj2):
                    print(obj, 'currently colliding with', obj2)

        window.render_line([100, 100], [300, 300], 64, Color.BLACK, dash=40, gap=20)
        window.update()
        time.tick(settings.framerate)


if __name__ == '__main__':
    mainloop()
