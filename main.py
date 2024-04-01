from copy import deepcopy
import random

import graphics
from graphics import Window, InputType

import physics
from physics import Vector2, Point2, Object

import city
from city import Building

import igtime

import settings


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
    window = graphics.Window([400, 400], 'Пригожин женя')
    camera = Camera(shape=[400, 400])
    time = igtime.Time()

    running = True
    objects: list[Object] = []

    for index in range(10):
        building = Building(
            edge_position=(0, 200 * index),
            #rotation=random.randint(0, 20),
            sprite=graphics.Sprite('assets/images/sprites/buildings/test_building.png'),
            height=5,
            roof_sprite=graphics.Sprite('assets/images/sprites/buildings/test_roof.png')
        )

        objects.append(building)

    while running:
        for event in window.get_input():
            match event:
                case InputType.LMB:
                    objects[0].set_position(
                        camera.get_global_position(Vector2(*window.get_mouse_position())))
                case InputType.RMB:
                    objects[1].set_position(
                        camera.get_global_position(Vector2(*window.get_mouse_position())))

                case InputType.W:
                    camera.position += Vector2(0, -2)
                case InputType.A:
                    camera.position += Vector2(-2, 0)
                case InputType.S:
                    camera.position += Vector2(0, 2)
                case InputType.D:
                    camera.position += Vector2(2, 0)

                case InputType.QUIT:
                    running = False

        window.clear()
        for obj in objects:
            obj.render_to(window, camera)

            for obj2 in objects:
                if obj != obj2 and obj.is_colliding_with(obj2):
                    print(obj, 'currently colliding with', obj2)

        window.update()
        time.tick(settings.framerate)


if __name__ == '__main__':
    mainloop()
