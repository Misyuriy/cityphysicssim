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
        return city.Building(edge_position=position, rotation=rotation, sprite=self.sprite, height=height, roof_sprite=self.roof_sprite)


class Blueprints:
    t1_4x1 = BuildingBlueprint(
        Sprite(path='assets/images/sprites/buildings/test_building.png'),
        Sprite(path='assets/images/sprites/buildings/test_roof.png'))


class Map:
    def __init__(self, buildings: list[city.Building]):
        self.buildings: list[city.Building] = buildings

    def get_objects(self):
        return self.buildings


test_map = Map(
    buildings=[
        Blueprints.t1_4x1.get_building([0, 0], height=7),
        Blueprints.t1_4x1.get_building([400, 192], rotation=90, height=3),
        Blueprints.t1_4x1.get_building([0, 384], height=5),
    ]
)