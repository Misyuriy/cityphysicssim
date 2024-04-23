import math

import settings
from settings import Color


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
        return Vector2(self.x * n, self.y * n)

    def normalize(self):
        return Vector2(self.x / abs(self), self.y / abs(self))

    def rotate(self, degrees: float):
        sine = math.sin(math.radians(degrees))
        cosine = math.cos(math.radians(degrees))

        return Vector2(self.x * cosine - self.y * sine, self.x * sine + self.y * cosine)

    def get_rotation(self):
        return math.degrees(math.atan2(self.y, self.x)) - 90

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


def intersect(p1: Vector2, p2: Vector2, m1: Vector2, m2: Vector2):
    p1p2 = Vector2(p1, p2)
    p1m1 = Vector2(p1, m1)
    p1m2 = Vector2(p1, m2)

    m1m2 = Vector2(m1, m2)
    m1p1 = Vector2(m1, p1)
    m1p2 = Vector2(m1, p2)

    if (p1p2.cross_product(p1m2) * p1p2.cross_product(p1m1) < 0
            and
            m1m2.cross_product(m1p2) * m1m2.cross_product(m1p1) < 0):
        return True
    else:
        return False


def simplify_angle(angle: float):
    angle = (angle / abs(angle)) * (abs(angle) % 360)
    if abs(angle) > 180:
        angle = -(angle / abs(angle)) * (360 - abs(angle))
    return angle


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
            edge_position = render_position - 0.5 * rotated_shape

            window.render(rotated_image, edge_position)
        else:
            edge_position = render_position - 0.5 * self.sprite.get_shape()
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
                 radius: float = None,
                 mass: float = 1):

        super().__init__(sprite, position, rotation, name)

        self.radius: float
        if radius:
            self.radius = radius
        else:
            self.radius = min([sprite.get_shape().x, sprite.get_shape().y]) // 2

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

        self.position += delta * self.linear_velocity
        self.rotation += delta * self.angular_velocity

    def apply_force(self, linear_force: Vector2 = Vector2(0, 0), angular_force: float = 0):
        self.linear_velocity += (1 / self.mass) * linear_force
        self.angular_velocity += (1 / self.mass) * angular_force

    def is_colliding_with(self, other):
        if hasattr(other, 'radius'):
            if self.position.dist(other.position) <= self.radius + other.radius:
                return True

        elif hasattr(other, 'rect'):
            a, b, c, d = other.get_vertices()
            segments = [(a, b), (b, c), (c, d), (d, a)]

            r1 = self.position
            r2 = self.position + (self.radius * (other.position - self.position).normalize())

            for segment in segments:
                if intersect(r1, r2, segment[0], segment[1]):
                    return True

        return False

    def render_to(self, window, camera):
        super().render_to(window, camera)

        if self.render_hitbox:
            render_position = camera.get_relative_position(self.position)
            window.render_circle(self.radius, render_position, color=(255, 0, 0))


class PhysicsStaticRect(Object):
    def __init__(self,
                 sprite,
                 position: tuple | list | Point2 | Vector2,
                 rotation: float = 0,
                 name: str = 'PhysicsStaticRect',
                 rect: Vector2 = None,
                 schematic_color: tuple | list = Color.sBUILDING
                 ):
        super().__init__(sprite, position, rotation, name)

        self.rect: Vector2
        if rect:
            self.rect = rect
        else:
            self.rect = Vector2(*self.sprite.get_shape())

        self.render_hitbox = settings.render_hitbox
        self.schematic_color = schematic_color

    def get_vertices(self, rotation_modifier: float = 0, scale_modifier: float = 1):
        edge_position = self.position + -0.5 * scale_modifier * self.rect.rotate(self.rotation)
        a = edge_position
        b = a + Vector2(scale_modifier * self.rect.x, 0).rotate(self.rotation + rotation_modifier)
        c = b + Vector2(0, scale_modifier * self.rect.y).rotate(self.rotation + rotation_modifier)
        d = a + Vector2(0, scale_modifier * self.rect.y).rotate(self.rotation + rotation_modifier)

        return a, b, c, d

    def is_colliding_with(self, other):
        a, b, c, d = self.get_vertices()
        segments = [(a, b), (b, c), (c, d), (d, a)]

        if hasattr(other, 'radius'):
            r1 = other.position
            r2 = other.position + (other.radius * (self.position - other.position).normalize())

            for segment in segments:
                if intersect(r1, r2, segment[0], segment[1]):
                    return True

        elif hasattr(other, 'rect'):
            a2, b2, c2, d2 = other.get_vertices()
            segments2 = [(a2, b2), (b2, c2), (c2, d2), (d2, a2)]

            for segment1 in segments:
                for segment2 in segments2:
                    if intersect(segment1[0], segment1[1], segment2[0], segment2[1]):
                        return True

        return False

    def render_to(self, window, camera):
        if camera.schematic:
            vertices = self.get_vertices()
            vertices = [camera.get_relative_position(vertex) for vertex in vertices]

            window.render_polygon(vertices, self.schematic_color)
            return

        super().render_to(window, camera)

        vertices = self.get_vertices()

        if self.render_hitbox:
            window.render_circle(radius=10, position=camera.get_relative_position(vertices[0]), color=Color.RED)
            window.render_circle(radius=10, position=camera.get_relative_position(vertices[1]), color=Color.GREEN)
            window.render_circle(radius=10, position=camera.get_relative_position(vertices[2]), color=Color.BLUE)
            window.render_circle(radius=10, position=camera.get_relative_position(vertices[3]), color=Color.YELLOW)


class PhysicsDynamicRect(PhysicsStaticRect):
    def __init__(self,
                 sprite,
                 position: tuple | list | Point2 | Vector2,
                 rotation: float = 0,
                 name: str = 'PhysicsDynamicRect',
                 rect: Vector2 = None,
                 mass: float = 1,
                 schematic_color: tuple | list = Color.sBUILDING
                 ):

        super().__init__(sprite, position, rotation, name, rect, schematic_color)

        self.mass: float = mass

        self.linear_velocity: Vector2 = Vector2(0, 0)
        self.angular_velocity: float = 0

        self.linear_torque: float = mass * settings.linear_mu
        self.angular_torque: float = mass * settings.angular_mu

    def update(self, delta, collisions: list[Object] = None):
        if abs(self.linear_velocity) > delta * self.linear_torque:
            self.linear_velocity -= delta * self.linear_torque * self.linear_velocity.normalize()
        else:
            self.linear_velocity = Vector2(0, 0)

        if abs(self.angular_velocity) > delta * self.angular_torque:
            self.angular_velocity -= delta * self.angular_torque * self.angular_velocity / abs(self.angular_velocity)
        else:
            self.angular_velocity = 0

        self.position += delta * self.linear_velocity
        self.rotation += delta * self.angular_velocity

    def apply_force(self, linear_force: Vector2 = Vector2(0, 0), angular_force: float = 0):
        self.linear_velocity += (1 / self.mass) * linear_force
        self.angular_velocity += (1 / self.mass) * angular_force


class PhysicsCircleAgent(PhysicsDynamicCircle):
    def __init__(self,
                 sprite,
                 position: tuple | list | Point2 | Vector2,
                 rotation: float = 0,
                 linear_acceleration: float = 1,
                 angular_acceleration: float = 1,
                 name: str = 'PhysicsCircleAgent',
                 radius: float = None,
                 mass: float = 1,
                 schematic_color: tuple | list = Color.sBUILDING
                 ):
        super().__init__(sprite, position, rotation, name, radius, mass)

        self.linear_acceleration: float = linear_acceleration
        self.angular_acceleration: float = angular_acceleration

        self.desired_velocity: Vector2 = Vector2(0, 0)

        self.render_velocities = settings.render_velocities

    def update(self, delta, collisions: list[Object] = None):
        desired_angular_velocity = simplify_angle(self.desired_velocity.get_rotation() - self.rotation)

        correction_angular_velocity = desired_angular_velocity - self.angular_velocity
        if abs(correction_angular_velocity) > self.angular_acceleration * delta:
            correction_angular_velocity = (correction_angular_velocity / abs(
                correction_angular_velocity)) * self.angular_acceleration * delta
        self.angular_velocity += correction_angular_velocity

        correction_vector = self.desired_velocity - self.linear_velocity
        if abs(self.linear_velocity - self.desired_velocity) > self.linear_acceleration * delta:
            correction_vector = self.linear_acceleration * delta * correction_vector.normalize()
        self.linear_velocity += correction_vector

        super().update(delta, collisions)

    def set_desired_velocity(self, new_desired_velocity: Vector2):
        self.desired_velocity = Vector2(new_desired_velocity)

    def render_to(self, window, camera):
        super().render_to(window, camera)
        if self.render_velocities:
            start = camera.get_relative_position(self.position)

            if abs(self.desired_velocity):
                end = start + self.desired_velocity
                window.render_line(start, end, color=Color.RED)

                end = start + Vector2(0, 64).rotate(self.desired_velocity.get_rotation())
                window.render_line(start, end, color=Color.GREEN)

            if abs(self.linear_velocity):
                end = start + self.linear_velocity
                window.render_line(start, end, color=Color.BLACK)

                end = start + Vector2(0, 64).rotate(self.rotation)
                window.render_line(start, end, color=Color.YELLOW)


class PhysicsRectAgent(PhysicsDynamicRect):
    def __init__(self,
                 sprite,
                 position: tuple | list | Point2 | Vector2,
                 rotation: float = 0,
                 linear_acceleration: float = 1,
                 angular_acceleration: float = 1,
                 name: str = 'PhysicsRectAgent',
                 rect: Vector2 = None,
                 mass: float = 1,
                 schematic_color: tuple | list = Color.sBUILDING
                 ):
        super().__init__(sprite, position, rotation, name, rect, mass, schematic_color)

        self.linear_acceleration: float = linear_acceleration
        self.angular_acceleration: float = angular_acceleration

        self.desired_velocity: Vector2 = Vector2(0, 0)

        self.render_velocities = settings.render_velocities

    def update(self, delta, collisions: list[Object] = None):
        desired_angular_velocity = simplify_angle(self.desired_velocity.get_rotation() - self.rotation)

        correction_angular_velocity = desired_angular_velocity - self.angular_velocity
        if abs(correction_angular_velocity) > self.angular_acceleration * delta:
            correction_angular_velocity = (correction_angular_velocity / abs(
                correction_angular_velocity)) * self.angular_acceleration * delta
        self.angular_velocity += correction_angular_velocity

        projection_length = -self.desired_velocity.rotate(-self.rotation + 90).x
        projection = Vector2(0, projection_length).rotate(self.rotation)

        correction_vector = projection - self.linear_velocity
        if abs(correction_vector) > self.linear_acceleration * delta:
            correction_vector = self.linear_acceleration * delta * correction_vector.normalize()
        self.linear_velocity += correction_vector

        super().update(delta, collisions)

    def set_desired_velocity(self, new_desired_velocity: Vector2):
        self.desired_velocity = Vector2(new_desired_velocity)

    def render_to(self, window, camera):
        super().render_to(window, camera)
        if self.render_velocities:
            start = camera.get_relative_position(self.position)

            if abs(self.desired_velocity):
                end = start + camera.schematic_scale * self.desired_velocity
                window.render_line(start, end, color=Color.RED)

                projection_length = -self.desired_velocity.rotate(-self.rotation + 90).x
                projection = Vector2(0, projection_length).rotate(self.rotation)
                end = start + camera.schematic_scale * projection
                window.render_line(start, end, color=Color.GREEN)

            if abs(self.linear_velocity):
                end = start + camera.schematic_scale * self.linear_velocity
                window.render_line(start, end, color=Color.BLACK)

                end = start + camera.schematic_scale * Vector2(0, 64).rotate(self.rotation)
                window.render_line(start, end, color=Color.YELLOW)
