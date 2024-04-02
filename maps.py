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
        return city.Building(sprite=self.sprite, edge_position=position, rotation=rotation, height=height, roof_sprite=self.roof_sprite)


class Blueprints:
    t1_4x1 = BuildingBlueprint(
        Sprite(path='assets/images/sprites/buildings/test_building.png'),
        Sprite(path='assets/images/sprites/buildings/test_roof.png'))


class Map:
    def __init__(self, buildings: list[city.Building], road_joints: list[Vector2], road_matrix: list[list]):
        self.buildings: list[city.Building] = buildings

        self.road_joints: list[Vector2] = road_joints
        self.road_matrix: list[list] = road_matrix

    def get_objects(self):
        return self.buildings

    def get_roads(self):
        return city.RoadGraph(self.road_joints, self.road_matrix)


test_map = Map(
    buildings=[
        Blueprints.t1_4x1.get_building(position=[300, -180], height=7),
    ],
    road_joints=[Vector2(0, 0), Vector2(600, 600), Vector2(0, 600), Vector2(600, 0)],
    road_matrix=[[0, 0, 0, 2],
                 [0, 0, 0, 0],
                 [0, 1, 0, 1],
                 [2, 0, 1, 0]]
)
