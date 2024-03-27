import graphics
from graphics import Window, InputType

import physics
from physics import Object


def mainloop():
    window = graphics.Window([400, 400], 'Пригожин женя')

    running = True
    objects: list[Object] = []

    objects.append(Object(position=(200, 200)))

    while running:
        for event in window.get_input():
            if event == InputType.QUIT:
                running = False

            if event == InputType.LMB_DOWN:
                objects[0].set_position(window.get_mouse_position())

        window.clear()
        for obj in objects:
            obj.render_to(window)

        window.update()


if __name__ == '__main__':
    mainloop()
