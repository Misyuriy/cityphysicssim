import graphics
import settings
import maps

from game import Game


def mainloop():
    window = graphics.Window([600, 600], 'Physics test')
    game = Game(window, maps.test_big_map, input_handling='PHYSICS_TEST')

    while game.running:
        game.update()


if __name__ == '__main__':
    mainloop()
