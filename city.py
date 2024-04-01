import graphics
from graphics import Sprite

import physics
from physics import Point2, Vector2


class Building(physics.PhysicsStaticRect):
    def __init__(self,
                 edge_position: tuple | list | Point2 | Vector2 = Vector2(0, 0),
                 rotation: float = 0,
                 sprite: Sprite = graphics.DEFAULT_SPRITE,
                 name: str = 'Building',
                 rect: Vector2 = None,
                 height: int = 1
                 ):
        super().__init__(edge_position, rotation, sprite, name, rect)

        self.height = height

    def render_to(self, window: graphics.Window, camera):
        super().render_to(window, camera)

        relative_position = camera.get_relative_position(self.position)

        parallax = (1 / 8) * (camera.get_center_position() - self.position)

        for floor in range(self.height):
            floor_sprite, floor_shape = self.sprite.get_scaled_image((1.1 ** floor) * Vector2(*self.sprite.get_shape()))

            edge_position = relative_position - 0.5 * Vector2(*floor_shape)
            edge_position -= floor * Vector2(parallax)

            window.render(floor_sprite, edge_position)
