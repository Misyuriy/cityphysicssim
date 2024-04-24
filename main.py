import graphics
import settings
import maps

from game import Game


def mainloop():
    window = graphics.Window([600, 600], 'City traffic simulator')
    game = Game(window, maps.editor_new_map)

    while game.running:
        game.update()

    if settings.print_map_on_quit:
        game.print_map()


if __name__ == '__main__':
    mainloop()
