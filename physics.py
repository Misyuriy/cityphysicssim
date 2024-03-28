import math

import graphics
from graphics import Sprite


class Point2:
    def __init__(self, x, y=None, polar=False):
        if isinstance(x, Point2):
            self.x = x.x
            self.y = x.y
            return

        if polar:
            self.x = x * math.cos(y)
            self.y = x * math.sin(y)
        else:
            self.x = x
            self.y = y

    def __abs__(self) -> float:
        return math.hypot(self.x, self.y)

    def __len__(self):
        return 2
    def __iter__(self):
        return iter([self.x, self.y])
    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

    def dist(self, x: float = None, y: float = None) -> float:
        if not x and not y:
            return abs(self)

        if isinstance(x, Point2):
            return math.hypot(abs(x.x - self.x), abs(x.y - self.y))

        return math.hypot(abs(x - self.x), abs(y - self.y))


class Vector2(Point2):
    def __init__(self, *args):
        match len(args):
            case 1:
                super().__init__(args[0])
            case 2:
                a, b = args
                if all(map(lambda x: isinstance(x, Point2), args)):
                    super().__init__(b.x - a.x, b.y - a.y)
                else:
                    super().__init__(a, b)
            case 3:
                super().__init__(*args)
            case 4:
                ax, ay, bx, by = args
                super().__init__(bx - ax, by - ay)

    def dot_product(self, other):
        return self.x * other.x + self.y * other.y

    def cross_product(self, other):
        return self.x * other.y - self.y * other.x

    def mul(self, n: int):
        self.x *= n
        self.y *= n

        return self

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __rsub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        return self.dot_product(other)

    def __xor__(self, other):
        return self.cross_product(other)

    def __rmul__(self, other):
        return self.mul(other)


class Object:
    def __init__(self,
                 position: tuple | list | Point2 | Vector2 = Vector2(0, 0),
                 rotation: float = 0,
                 sprite: Sprite = graphics.DEFAULT_SPRITE):
        self.position: Vector2 = Vector2(*position)
        self.rotation: float = rotation

        self.sprite: Sprite = sprite

    def render_to(self, window: graphics.Window):
        if self.rotation:
            rotated_image, rotated_shape = self.sprite.get_rotated_image(self.rotation)
            edge_position = self.position - 0.5 * Vector2(*rotated_shape)

            window.render(rotated_image, edge_position)
        else:
            edge_position = self.position - 0.5 * Vector2(*self.sprite.get_shape())
            window.render(self.sprite.image, edge_position)

    def set_position(self, new_position: tuple | list | Point2 | Vector2):
        self.position = Vector2(*new_position)


class PhysicsDynamicCircle:
    def __init__(self):
        pass
