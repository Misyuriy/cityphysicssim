import graphics
from graphics import Window, InputType

import physics
from physics import Vector2, Point2, Object


class Camera:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Camera, cls).__new__(cls)
        return cls.instance

    def __init__(self,
                 position: tuple | list | Point2 | Vector2 = Vector2(0, 0),):
        self.position: Vector2 = Vector2(position)

    def get_relative_position(self, global_position: Vector2):
        return global_position - self.position

    def get_global_position(self, relative_position: Vector2):
        return relative_position + self.position


def mainloop():
    window = graphics.Window([400, 400], 'Пригожин женя')
    camera = Camera()

    running = True
    objects: list[Object] = []

    objects.append(physics.PhysicsDynamicCircle(
        position=(100, 100),
        radius=64,
        linear_torque=0,
        angular_torque=0
        ))

    objects.append(physics.PhysicsStaticRect(
        edge_position=(300, 300),
        sprite=graphics.Sprite('assets/images/sprites/long_sprite.png')
    ))

    while running:
        objects[0].rotation += 0.1
        for event in window.get_input():
            match event:
                case InputType.LMB:
                    objects[0].set_position(
                        camera.get_global_position(Vector2(*window.get_mouse_position())))
                case InputType.RMB:
                    objects[1].set_position(
                        camera.get_global_position(Vector2(*window.get_mouse_position())))

                case InputType.W:
                    camera.position += Vector2(0, -1)
                case InputType.A:
                    camera.position += Vector2(-1, 0)
                case InputType.S:
                    camera.position += Vector2(0, 1)
                case InputType.D:
                    camera.position += Vector2(1, 0)

                case InputType.QUIT:
                    running = False

        window.clear()
        for obj in objects:
            obj.render_to(window, camera)

            for obj2 in objects:
                if obj != obj2 and obj.is_colliding_with(obj2):
                    print(obj, 'currently colliding with', obj2)

        window.update()


if __name__ == '__main__':
    mainloop()
