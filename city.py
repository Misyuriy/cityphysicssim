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
                 roof_sprite: Sprite = None,
                 schematic_color: tuple | list = Color.sBUILDING
                 ):
        super().__init__(sprite, position, rotation, name, rect, schematic_color)

        self.height = height
        self.roof_sprite = roof_sprite

        self.schematic_color = schematic_color

    def render_to(self, window: graphics.Window, camera):
        super().render_to(window, camera)
        if camera.schematic:
            return

        floor_sprite = self.sprite

        relative_position = camera.get_relative_position(self.position)

        if self.rotation:
            rotated_image, rotated_shape = floor_sprite.get_rotated_image(self.rotation)

            floor_sprite = Sprite(image=rotated_image)

        parallax = settings.parallax_moving_step * (camera.get_center_position() - self.position)

        for floor in range(1, self.height):
            floor_image, floor_shape = floor_sprite.get_scaled_image(
                (settings.parallax_scaling_step ** floor) * floor_sprite.get_shape()
            )
            edge_position = relative_position - 0.5 * floor_shape

            edge_position -= floor * parallax

            window.render(floor_image, edge_position)

        if self.roof_sprite:
            rotated_image, rotated_shape = self.roof_sprite.get_rotated_image(self.rotation)
            roof_sprite = Sprite(image=rotated_image)

            roof_image, roof_shape = roof_sprite.get_scaled_image(
                (settings.parallax_scaling_step ** self.height) * rotated_shape
            )
            edge_position = relative_position - 0.5 * roof_shape

            edge_position -= self.height * parallax

            window.render(roof_image, edge_position)


class RoadGraph:
    def __init__(self, joints: list[Vector2], matrix: list[list], color_variant: int = 0):
        self.joints: list[Vector2] = joints

        self.selected_joint: int = -1
        self.selected_road: list[int, int] = [-1, -1]
        self.n_joints = len(joints)

        self.matrix: list[list] = matrix

        self.s_joint_color: tuple
        self.s_road_color: tuple
        self.road_color: tuple

        match color_variant:
            case 0:
                self.s_joint_color = Color.sVERTEX
                self.s_road_color = Color.sROAD
                self.road_color = Color.DARK_ASPHALT
            case 1:
                self.s_joint_color = Color.sSIDEWALK_VERTEX
                self.s_road_color = Color.sSIDEWALK
                self.road_color = Color.ASPHALT
            case _:
                raise 'invalid color variant for RoadGraph: ' + str(color_variant)

    def get_joint_radius(self, index: int):
        max_roads = max(self.matrix[index])
        return settings.road_size * max_roads

    def add_joint(self, position: Vector2, connected_index: int, connection_to_new: int = 1, connection_from_new: int = 1):
        self.joints.append(position)
        self.n_joints += 1

        self.matrix = [i + [0] for i in self.matrix]
        self.matrix.append([0] * self.n_joints)

        self.matrix[connected_index][-1] = connection_to_new
        self.matrix[-1][connected_index] = connection_from_new

    def render_to(self, window: graphics.Window, camera):
        for i in range(self.n_joints):
            for j in range(self.n_joints):
                if not (self.matrix[i][j] or self.matrix[j][i]):
                    continue

                self.render_road_to(window, camera, i, j)

        for index, joint in enumerate(self.joints):
            max_roads = max(self.matrix[index])

            if camera.schematic:
                color = self.s_joint_color
                if index == self.selected_joint:
                    color = Color.sSELECTED

                window.render_circle(camera.schematic_scale * settings.road_size * max_roads,
                                     camera.get_relative_position(joint), color)
            else:
                window.render_circle(settings.road_size * max_roads, camera.get_relative_position(joint), self.road_color)

    def render_road_to(self, window: graphics.Window, camera, i: int, j: int):
        relative_position = camera.get_relative_position(Vector2(0, 0))

        if camera.schematic:
            color = self.s_road_color
            if [i, j] == self.selected_road or [j, i] == self.selected_road:
                color = Color.sSELECTED
            window.render_line(relative_position + (camera.schematic_scale * self.joints[i]),
                               relative_position + (camera.schematic_scale * self.joints[j]),
                               width=camera.schematic_scale * settings.road_size * (
                                           self.matrix[i][j] + self.matrix[j][i]),
                               color=color)
            return

        window.render_line(relative_position + self.joints[i],
                           relative_position + self.joints[j],
                           width=settings.road_size * (self.matrix[i][j] + self.matrix[j][i]),
                           color=self.road_color)
        if self.road_color == Color.ASPHALT:
            return

        window.render_line_edges(relative_position + self.joints[i],
                                 relative_position + self.joints[j],
                                 width=settings.road_size * (self.matrix[i][j] + self.matrix[j][i]),
                                 color=Color.MARKING_WHITE,
                                 edge_width=settings.marking_size)

        match self.matrix[i][j] + self.matrix[j][i]:
            case 1:
                pass
            case 2:
                window.render_line(relative_position + self.joints[i],
                                   relative_position + self.joints[j],
                                   width=settings.marking_size,
                                   color=Color.MARKING_WHITE,
                                   dash=settings.dotted_marking[0],
                                   gap=settings.dotted_marking[1])
            case _:
                window.render_line(relative_position + self.joints[i],
                                   relative_position + self.joints[j],
                                   width=settings.marking_size,
                                   color=Color.MARKING_WHITE)
                for n_roads in range(2, self.matrix[i][j] + self.matrix[j][i], 2):
                    window.render_line_edges(relative_position + self.joints[i],
                                             relative_position + self.joints[j],
                                             width=settings.road_size * n_roads,
                                             color=Color.MARKING_WHITE,
                                             edge_width=settings.marking_size,
                                             dash=settings.dotted_marking[0],
                                             gap=settings.dotted_marking[1])
