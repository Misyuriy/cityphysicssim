import graphics
from graphics import Sprite

import physics
from physics import Point2, Vector2

import settings


class Building(physics.PhysicsStaticRect):
    def __init__(self,
                 sprite: Sprite,
                 edge_position: tuple | list | Point2 | Vector2 = Vector2(0, 0),
                 rotation: float = 0,
                 name: str = 'Building',
                 rect: Vector2 = None,
                 height: int = 1,
                 roof_sprite: Sprite = None
                 ):
        super().__init__(sprite, edge_position, rotation, name, rect)

        self.height = height
        self.roof_sprite = roof_sprite

    def render_to(self, window: graphics.Window, camera):
        super().render_to(window, camera)

        floor_sprite = self.sprite

        relative_position = camera.get_relative_position(self.position)

        if self.rotation:
            rotated_image, rotated_shape = floor_sprite.get_rotated_image(self.rotation)

            floor_sprite = Sprite(image=rotated_image)

        parallax = settings.parallax_moving_step * (camera.get_center_position() - self.position)

        for floor in range(1, self.height):
            floor_image, floor_shape = floor_sprite.get_scaled_image(
                (settings.parallax_scaling_step ** floor) * Vector2(*floor_sprite.get_shape())
            )
            edge_position = relative_position - 0.5 * Vector2(*floor_shape)

            edge_position -= floor * Vector2(parallax)

            window.render(floor_image, edge_position)

        if self.roof_sprite:
            rotated_image, rotated_shape = self.roof_sprite.get_rotated_image(self.rotation)
            roof_sprite = Sprite(image=rotated_image)

            roof_image, roof_shape = roof_sprite.get_scaled_image(
                (settings.parallax_scaling_step ** self.height) * Vector2(*rotated_shape)
            )
            edge_position = relative_position - 0.5 * Vector2(*roof_shape)

            edge_position -= self.height * Vector2(parallax)

            window.render(roof_image, edge_position)

