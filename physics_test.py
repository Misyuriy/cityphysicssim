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

from main import Camera


def get_selected(click: Vector2, objects: list[Object], camera: Camera):
    global_click = camera.get_global_position(click)

    for obj in objects:
        if obj.position.dist(global_click.x, global_click.y) <= obj.radius:
            return obj

    return None


def mainloop():
    window = Window([600, 600], 'Пригожин женя тестирует физику')
    camera = Camera(position=[0, 0], shape=[600, 600])
    time = igtime.Time()

    running = True
    dynamic_objects: list[Object] = [
        physics.PhysicsDynamicCircle(
            Sprite(path='assets/images/sprites/default_sprite.png'),
            Vector2(0, 0),
            name='Circle1',
            radius=64,
            mass=5
        )
    ]
    objects: list[Object] = dynamic_objects

    dynamic_objects[0].apply_force(linear_force=Vector2(250, 250), angular_force=200)

    selection: Object = None

    delta = 1
    while running:
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

                case InputType.LMB:
                    new_selection = get_selected(window.get_mouse_position(), dynamic_objects, camera)
                    if new_selection:
                        if selection:
                            selection.render_hitbox = False

                        selection = new_selection
                        selection.render_hitbox = True

                    elif selection:
                        selection.render_hitbox = False
                        selection = None

                case InputType.RMB:
                    if selection:
                        global_click = camera.get_global_position(window.get_mouse_position())
                        selection.apply_force(linear_force=global_click - selection.position)

                        selection.render_hitbox = False
                        selection = None

                case InputType.SCROLL_UP:
                    if selection:
                        selection.apply_force(angular_force=50)
                case InputType.SCROLL_DOWN:
                    if selection:
                        selection.apply_force(angular_force=-50)

                case InputType.QUIT:
                    running = False

        window.clear()

        for obj in dynamic_objects:
            obj.update(delta)

        for obj in objects:
            obj.render_to(window, camera)

            for obj2 in objects:
                if obj != obj2 and obj.is_colliding_with(obj2):
                    print(obj, 'currently colliding with', obj2)

        window.update()
        delta = time.tick(settings.framerate)


mainloop()
