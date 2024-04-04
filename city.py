import graphics
from graphics import Sprite

import physics
from physics import Point2, Vector2

import settings
from settings import Color


class Building(physics.PhysicsStaticRect):
    def __init__(self,
                 sprite: Sprite,
                 position: tuple | list | Point2 | Vector2 = Vector2(0, 0),
                 rotation: float = 0,
                 name: str = 'Building',
                 rect: Vector2 = None,
                 height: int = 1,
                 roof_sprite: Sprite = None
                 ):
        super().__init__(sprite, position, rotation, name, rect)

        self.height = height
        self.roof_sprite = roof_sprite

    def render_to(self, window: graphics.Window, camera):
        super().render_to(window, camera)
        if camera.simplified:
            return

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


class RoadGraph:
    def __init__(self, joints: list[Vector2], matrix: list[list]):
        self.joints: list[Vector2] = joints
        self.n_joints = len(joints)

        self.matrix: list[list] = matrix

    def render_to(self, window: graphics.Window, camera):
        relative_position = camera.get_relative_position(Vector2(0, 0))

        for i in range(self.n_joints):
            for j in range(self.n_joints):
                if not (self.matrix[i][j] or self.matrix[j][i]):
                    continue

                if camera.simplified:
                    window.render_line(relative_position + (camera.simplified_scale * Vector2(self.joints[i])),
                                       relative_position + (camera.simplified_scale * Vector2(self.joints[j])),
                                       width=camera.simplified_scale * settings.road_size * (self.matrix[i][j] + self.matrix[j][i]),
                                       color=Color.sROAD)
                    continue

                window.render_line(relative_position + self.joints[i],
                                   relative_position + self.joints[j],
                                   width=settings.road_size * (self.matrix[i][j] + self.matrix[j][i]),
                                   color=Color.ROAD)
                window.render_line_edges(relative_position + self.joints[i],
                                         relative_position + self.joints[j],
                                         width=settings.road_size * (self.matrix[i][j] + self.matrix[j][i]),
                                         color=Color.WHITE,
                                         edge_width=settings.marking_size)

                match self.matrix[i][j] + self.matrix[j][i]:
                    case 1:
                        pass
                    case 2:
                        window.render_line(relative_position + self.joints[i],
                                           relative_position + self.joints[j],
                                           width=settings.marking_size,
                                           color=Color.WHITE,
                                           dash=settings.dotted_marking[0],
                                           gap=settings.dotted_marking[1])
                    case _:
                        window.render_line(relative_position + self.joints[i],
                                           relative_position + self.joints[j],
                                           width=settings.marking_size,
                                           color=Color.WHITE)
                        for n_roads in range(2, self.matrix[i][j] + self.matrix[j][i], 2):
                            window.render_line_edges(relative_position + self.joints[i],
                                                     relative_position + self.joints[j],
                                                     width=settings.road_size * n_roads,
                                                     color=Color.WHITE,
                                                     edge_width=settings.marking_size,
                                                     dash=settings.dotted_marking[0],
                                                     gap=settings.dotted_marking[1])

        for index, joint in enumerate(self.joints):
            max_roads = max(self.matrix[index])

            if camera.simplified:
                window.render_circle(camera.simplified_scale * settings.road_size * max_roads,
                                     relative_position + (camera.simplified_scale * Vector2(joint)), Color.sVERTEX)
            else:
                window.render_circle(settings.road_size * max_roads, relative_position + joint, Color.ROAD)
