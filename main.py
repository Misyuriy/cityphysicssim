import graphics
from graphics import Window, InputType

import physics
from physics import Object


def mainloop():
    window = graphics.Window([400, 400], 'Пригожин женя')

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
        objects[1].rotation -= 0.1
        for event in window.get_input():
            if event == InputType.QUIT:
                running = False

            if event == InputType.LMB_DOWN:
                objects[0].set_position(window.get_mouse_position())

            if event == InputType.RMB_DOWN:
                objects[1].set_position(window.get_mouse_position())

        window.clear()
        for obj in objects:
            obj.render_to(window)

            for obj2 in objects:
                if obj != obj2 and obj.is_colliding_with(obj2):
                    print(obj, 'currently colliding with', obj2)

        window.update()


if __name__ == '__main__':
    mainloop()
