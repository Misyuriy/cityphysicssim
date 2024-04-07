import graphics
import settings
import maps

from game import Game


def mainloop():
    window = graphics.Window([600, 600], 'City traffic simulator')
    game = Game(window, maps.test_big_map)

    while game.running:
        game.update()


if __name__ == '__main__':
    mainloop()
