import math

import settings


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

    def normalize(self):
        return Vector2(self.x / abs(self), self.y / abs(self))

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
                 sprite,
                 position: tuple | list | Point2 | Vector2,
                 rotation: float,
                 name: str = 'Object'):
        self.position: Vector2 = Vector2(*position)
        self.rotation: float = rotation

        self.sprite = sprite
        self.name: str = name

    def render_to(self, window, camera):
        render_position = camera.get_relative_position(self.position)

        if self.rotation:
            rotated_image, rotated_shape = self.sprite.get_rotated_image(self.rotation)
            edge_position = render_position - 0.5 * Vector2(*rotated_shape)

            window.render(rotated_image, edge_position)
        else:
            edge_position = render_position - 0.5 * Vector2(*self.sprite.get_shape())
            window.render(self.sprite.image, edge_position)

    def set_position(self, new_position: tuple | list | Point2 | Vector2):
        self.position = Vector2(*new_position)

    def __str__(self):
        return self.name


class PhysicsDynamicCircle(Object):
    def __init__(self,
                 sprite,
                 position: tuple | list | Point2 | Vector2,
                 rotation: float = 0,
                 name: str = 'PhysicsDynamicCircle',
                 radius: float = 1,
                 mass: float = 1):

        super().__init__(sprite, position, rotation, name)

        self.radius: float = radius
        self.mass: float = mass

        self.linear_velocity: Vector2 = Vector2(0, 0)
        self.angular_velocity: float = 0

        self.linear_torque: float = mass * settings.linear_mu
        self.angular_torque: float = mass * settings.angular_mu

        self.render_hitbox = settings.render_hitbox

    def update(self, delta, collisions: list[Object] = None):
        if abs(self.linear_velocity) > delta * self.linear_torque:
            self.linear_velocity -= delta * self.linear_torque * self.linear_velocity.normalize()
        else:
            self.linear_velocity = Vector2(0, 0)

        if abs(self.angular_velocity) > delta * self.angular_torque:
            self.angular_velocity -= delta * self.angular_torque * self.angular_velocity / abs(self.angular_velocity)
        else:
            self.angular_velocity = 0

        self.position += delta * Vector2(self.linear_velocity)
        self.rotation += delta * self.angular_velocity

    def apply_force(self, linear_force: Vector2 = Vector2(0, 0), angular_force: float = 0):
        self.linear_velocity += (1 / self.mass) * linear_force
        self.angular_velocity += (1 / self.mass) * angular_force

    def is_colliding_with(self, other):
        if hasattr(other, 'radius'):
            if self.position.dist(other.position) <= self.radius + other.radius:
                return True
        elif hasattr(other, 'rect'):
            pass # написать расчет с прямоугольником
        return False

    def render_to(self, window, camera):
        super().render_to(window, camera)

        if self.render_hitbox:
            render_position = camera.get_relative_position(self.position)
            window.render_circle(self.radius, render_position, color=(255, 0, 0))


class PhysicsStaticRect(Object):
    def __init__(self,
                 sprite,
                 edge_position: tuple | list | Point2 | Vector2,
                 rotation: float = 0,
                 name: str = 'PhysicsStaticRect',
                 rect: Vector2 = None
                 ):
        super().__init__(sprite, edge_position, rotation, name)

        if rect:
            self.rect = rect
        else:
            self.rect = Vector2(*self.sprite.get_shape())

    def is_colliding_with(self, other):
        if hasattr(other, 'radius'):
            pass # написать расчет с радиусом
        elif hasattr(other, 'rect'):
            pass # написать расчет с прямоугольником
        return False
