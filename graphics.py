import pygame


class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)


class Sprite:
    def __init__(self, path: str = None, image: pygame.Surface = None):
        self.image: pygame.Surface

        # Either loads image from given path or directly from passed pygame.Surface
        if path:
            self.image = pygame.image.load(path)
        elif image:
            self.image = image

    def get_shape(self):
        return self.image.get_width(), self.image.get_height()

    def get_rotated_image(self, rotation: float):
        rotated_image = pygame.transform.rotate(self.image, rotation)
        new_shape = rotated_image.get_rect(center=rotated_image.get_rect().center)

        return rotated_image, new_shape

    def get_scaled_image(self, new_scale):
        scaled_image = pygame.transform.scale(self.image, list(new_scale))
        new_shape = scaled_image.get_rect(center=scaled_image.get_rect().center)

        return scaled_image, new_shape


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

        self.pressed_keys = set()

    def clear(self):
        self.display.fill('white')

    def _correctly_render_line(self, start, end, width, color):
        pass
        #pygame.draw.polygon(self.display, color,
                            #[[250, 110], [280, 150],
                             #[190, 190], [130, 130]])

    def render(self, image: pygame.Surface, position):
        self.display.blit(image, list(position))

    def render_circle(self, radius: float, position, color):
        pygame.draw.circle(self.display, color, list(position), radius)

    def render_line(self, start, end, width: int = 1, color: tuple | list = Color.WHITE, dash: float = 1, gap: float = 0):
        if gap:
            current_start = start

            while abs(current_start - start) < abs(end - start):
                current_end = current_start + dash * (end - start).normalize()
                if abs(current_end - start) > abs(end - start):
                    current_end = end

                pygame.draw.line(self.display, color, list(current_start), list(current_end), width)

                current_start = current_end + gap * (end - start).normalize()

        else:
            pygame.draw.line(self.display, color, list(start), list(end), width)

    def update(self):
        pygame.display.flip()

    def get_mouse_position(self):
        return pygame.mouse.get_pos()

    def get_input(self) -> list:
        relevant_events = []

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.pressed_keys.add(event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.pressed_keys.remove(event.button)

            elif event.type == pygame.KEYDOWN:
                self.pressed_keys.add(event.key)
            elif event.type == pygame.KEYUP:
                self.pressed_keys.remove(event.key)

            elif event.type in [pygame.QUIT]:
                relevant_events.append(event.type)

        return relevant_events + list(self.pressed_keys)


class InputType:
    QUIT = pygame.QUIT

    LMB = 1
    RMB = 3

    W = pygame.K_w
    A = pygame.K_a
    S = pygame.K_s
    D = pygame.K_d

    SCROLL_UP = 4
    SCROLL_DOWN = 5


DEFAULT_SPRITE = Sprite(path='assets/images/sprites/default_sprite.png')
