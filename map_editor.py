import graphics
import settings
import maps

from game import Game


def mainloop():
    window = graphics.Window([600, 600], 'Map editor')
    game = Game(window, maps.editor_new_map, input_handling='MAP_EDITOR')

    while game.running:
        game.update()


if __name__ == '__main__':
    mainloop()
