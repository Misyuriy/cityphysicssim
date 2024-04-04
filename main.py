import random

import graphics
from graphics import Sprite, Window, InputType
import physics
from physics import Vector2, Point2, Object

import city
from city import Building, RoadGraph

import igtime

import settings
from settings import Color

import maps


class Camera:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Camera, cls).__new__(cls)
        return cls.instance

    def __init__(self,
                 position: tuple | list | Point2 | Vector2 = Vector2(0, 0),
                 shape: tuple | list | Point2 | Vector2 = Vector2(0, 0),
                 simplified: bool = False):
        self.position: Vector2 = Vector2(*position)

        self.shape: Vector2 = Vector2(*shape)

        self.simplified: bool = simplified
        self.simplified_scale: float = 1

    def get_center_position(self):
        return self.position + (0.5 * Vector2(self.shape))

    def get_relative_position(self, global_position: Vector2):
        if self.simplified:
            return (self.simplified_scale * global_position) - self.position
        return global_position - self.position

    def get_global_position(self, relative_position: Vector2):
        if self.simplified:
            return (1 / self.simplified_scale) * (relative_position + self.position)
        return relative_position + self.position


def mainloop():
    window = Window([600, 600], 'Пригожин женя')
    camera = Camera(position=[0, -200], shape=[600, 600])
    time = igtime.Time()

    running = True
    dynamic_objects: list[Object] = []
    objects: list[Object] = maps.test_big_map.get_objects()
    roads: RoadGraph = maps.test_big_map.get_roads()

    shift_x_hold = False

    delta = 1
    while running:
        key_input = window.get_input()
        if InputType.X in key_input and InputType.SHIFT in key_input:
            if not shift_x_hold:
                camera.simplified = not camera.simplified
                camera.simplified_scale = 1
                shift_x_hold = True

        elif shift_x_hold:
            shift_x_hold = False

        for event in key_input:
            match event:
                case InputType.W:
                    camera.position.y -= 2
                case InputType.A:
                    camera.position.x -= 2
                case InputType.S:
                    camera.position.y += 2
                case InputType.D:
                    camera.position.x += 2

                case InputType.SCROLL_UP:
                    print('SCROLL UP')
                    if camera.simplified:
                        camera.simplified_scale -= 0.01
                case InputType.SCROLL_DOWN:
                    print('SCROLL DOWN')
                    if camera.simplified:
                        camera.simplified_scale += 0.01

                case InputType.QUIT:
                    running = False

        if camera.simplified:
            window.fill(Color.sDEFAULT)
        else:
            window.fill(Color.DEFAULT)

        if roads:
            roads.render_to(window, camera)

        for obj in dynamic_objects:
            obj.update(delta)

        for obj in objects:
            obj.render_to(window, camera)

            for obj2 in objects:
                if obj != obj2 and obj.is_colliding_with(obj2):
                    print(obj, 'currently colliding with', obj2)

        window.update()
        delta = time.tick(settings.framerate)


if __name__ == '__main__':
    mainloop()
