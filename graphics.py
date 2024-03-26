import pygame


class Window(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Window, cls).__new__(cls)
        return cls.instance

    def __init__(self, dimensions: list[int], caption: str = None):
        pygame.init()

        self.display = pygame.display.set_mode(dimensions)
        if caption:
            pygame.display.set_caption(caption)

    def get_input(self) -> list:
        return pygame.event.get()


class InputType:
    QUIT = pygame.QUIT

