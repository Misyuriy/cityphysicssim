import city

import graphics
from graphics import Sprite

import physics
from physics import Vector2


class BuildingBlueprint:
    def __init__(self, sprite: Sprite, roof_sprite: Sprite):
        self.sprite: Sprite = sprite
        self.roof_sprite: Sprite = roof_sprite

    def get_building(self, position: tuple | list | Vector2, rotation: float = 0, height: int = 1):
        return city.Building(sprite=self.sprite, position=position, rotation=rotation, height=height, roof_sprite=self.roof_sprite)


class Blueprints:
    t1_4x1 = BuildingBlueprint(
        Sprite(path='assets/images/sprites/buildings/test_building.png'),
        Sprite(path='assets/images/sprites/buildings/test_roof.png'))

    p1_5x2 = BuildingBlueprint(
        Sprite(path='assets/images/sprites/buildings/panel1_building.png'),
        Sprite(path='assets/images/sprites/buildings/panel1_roof.png'))

    p2_5x2 = BuildingBlueprint(
        Sprite(path='assets/images/sprites/buildings/panel2_building.png'),
        Sprite(path='assets/images/sprites/buildings/panel2_roof.png'))

    p1_11x2 = BuildingBlueprint(
        Sprite(path='assets/images/sprites/buildings/panel_long_building.png'),
        Sprite(path='assets/images/sprites/buildings/panel_long_roof.png'))


class Map:
    def __init__(self,
                 buildings: list[city.Building],
                 road_joints: list[Vector2],
                 road_matrix: list[list],
                 initial_camera_position: Vector2 = Vector2(0, 0)):
        self.buildings: list[city.Building] = buildings

        self.road_joints: list[Vector2] = road_joints
        self.road_matrix: list[list] = road_matrix

        self.initial_camera_position = initial_camera_position

    def get_objects(self):
        return self.buildings

    def get_roads(self):
        return city.RoadGraph(self.road_joints, self.road_matrix)


test_map = Map(
    buildings=[
        Blueprints.p2_5x2.get_building(position=[300, -300], height=7),
    ],
    road_joints=[Vector2(0, 0), Vector2(600, 600), Vector2(0, 600), Vector2(600, 0)],
    road_matrix=[[0, 0, 0, 2],
                 [0, 0, 0, 0],
                 [0, 1, 0, 1],
                 [2, 0, 1, 0]]
)

test_big_map = Map(
    buildings=[
        Blueprints.t1_4x1.get_building(position=[0, 0], height=7),
        Blueprints.t1_4x1.get_building(position=[600, 0], height=5),
        Blueprints.t1_4x1.get_building(position=[300, 400], height=3),
        Blueprints.t1_4x1.get_building(position=[900, 700], rotation=-45, height=5),
    ],
    road_joints=[Vector2(-400, 200),
                 Vector2(640, 200),
                 Vector2(2000, 200),
                 Vector2(1440, 1000)
                 ],
    road_matrix=[[0, 2, 0, 0],
                 [2, 0, 2, 1],
                 [0, 2, 0, 0],
                 [0, 1, 0, 0]]
)

editor_new_map = Map(
    buildings=[
        Blueprints.p2_5x2.get_building(position=[300, -300], height=7),
    ],
    road_joints=[Vector2(0, 0), Vector2(600, 600), Vector2(0, 600), Vector2(600, 0)],
    road_matrix=[[0, 0, 0, 2],
                 [0, 0, 1, 0],
                 [0, 1, 0, 1],
                 [2, 0, 1, 0]]
)
