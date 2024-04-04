import random

import graphics
from graphics import Sprite, Window, InputType, Color
import physics
from physics import Vector2, Point2, Object

import city
from city import Building, RoadGraph

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
        self.scale: float = 1

        self.shape: Vector2 = Vector2(*shape)

    def get_center_position(self):
        return self.position + (0.5 * Vector2(self.shape))

    def get_relative_position(self, global_position: Vector2):
        return global_position - self.position

    def get_global_position(self, relative_position: Vector2):
        return relative_position + self.position


def mainloop():
    window = Window([600, 600], 'Пригожин женя')
    camera = Camera(position=[0, -200], shape=[600, 600])
    time = igtime.Time()

    running = True
    dynamic_objects: list[Object] = []
    objects: list[Object] = maps.test_map.get_objects()
    #roads: RoadGraph = maps.test_map.get_roads()

    delta = 1
    while running:
        vertices = objects[0].get_vertices()

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

                case InputType.SCROLL_UP:
                    objects[0].rotation += 1
                case InputType.SCROLL_DOWN:
                    objects[0].rotation -= 1

                case InputType.QUIT:
                    running = False

        window.clear()
        #if roads:
        #    roads.render_to(window, camera)

        for obj in dynamic_objects:
            obj.update(delta)

        for obj in objects:
            obj.render_to(window, camera)

            for obj2 in objects:
                if obj != obj2 and obj.is_colliding_with(obj2):
                    print(obj, 'currently colliding with', obj2)

        window.render_circle(radius=10, position=camera.get_relative_position(vertices[0]), color=Color.RED)
        window.render_circle(radius=10, position=camera.get_relative_position(vertices[1]), color=Color.GREEN)
        window.render_circle(radius=10, position=camera.get_relative_position(vertices[2]), color=Color.BLUE)
        window.render_circle(radius=10, position=camera.get_relative_position(vertices[3]), color=Color.YELLOW)

        window.update()
        delta = time.tick(settings.framerate)


if __name__ == '__main__':
    mainloop()
