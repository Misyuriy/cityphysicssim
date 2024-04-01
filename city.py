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
        # написать эффект параллакс
