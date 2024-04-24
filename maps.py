import city

import graphics
from graphics import Sprite

import physics
from physics import Vector2, Object


class BuildingBlueprint:
    def __init__(self, sprite: Sprite, roof_sprite: Sprite):
        self.sprite: Sprite = sprite
        self.roof_sprite: Sprite = roof_sprite

    def get_building(self, position: tuple | list | Vector2, rotation: float = 0, height: int = 1, name='Building'):
        return city.Building(
            sprite=self.sprite,
            position=position,
            rotation=rotation,
            name=name,
            height=height,
            roof_sprite=self.roof_sprite
        )


class CarBlueprint:
    def __init__(self, sprite: Sprite, mass: float, max_speed: float, linear_acceleration: float = 100, angular_acceleration: float = 60):
        self.sprite: Sprite = sprite
        self.linear_acceleration = linear_acceleration
        self.angular_acceleration = angular_acceleration
        self.mass = mass
        self.max_speed = max_speed

    def get_car(self, position: tuple | list | Vector2, rotation: float = 0, name='Building'):
        return city.Car(
            sprite=self.sprite,
            position=position,
            rotation=rotation,
            linear_acceleration=self.linear_acceleration,
            angular_acceleration=self.angular_acceleration,
            name=name,
            mass=self.mass,
            max_speed=self.max_speed
        )


class Blueprints:
    # Buildings:
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

    # Cars:
    tt_1 = CarBlueprint(
        Sprite(path='assets/images/sprites/cars/test_truck.png'),
        mass=8,
        max_speed=200,
        linear_acceleration=200,
        angular_acceleration=120
    )


class Map:
    def __init__(self,
                 buildings: list[city.Building],
                 road_joints: list[Vector2],
                 road_matrix: list[list],
                 sidewalk_joints: list[Vector2],
                 sidewalk_matrix: list[list],
                 initial_camera_position: Vector2 = Vector2(0, 0),
                 other_static_objects: list[Object] = [],
                 other_dynamic_objects: list[Object] = []):
        self.buildings: list[city.Building] = buildings
        self.other_static_objects: list[Object] = other_static_objects
        self.other_dynamic_objects: list[Object] = other_dynamic_objects

        self.road_joints: list[Vector2] = road_joints
        self.road_matrix: list[list] = road_matrix

        self.sidewalk_joints: list[Vector2] = sidewalk_joints
        self.sidewalk_matrix: list[list] = sidewalk_matrix

        self.initial_camera_position = initial_camera_position

    def get_objects(self):
        return self.buildings + self.other_static_objects + self.other_dynamic_objects

    def get_static_objects(self):
        return self.buildings + self.other_static_objects

    def get_dynamic_objects(self):
        return self.other_dynamic_objects

    def get_roads(self):
        return city.RoadGraph(self.road_joints, self.road_matrix)

    def get_sidewalks(self):
        return city.RoadGraph(self.sidewalk_joints, self.sidewalk_matrix, color_variant=1)


physics_test_map = Map(
    buildings=[
    ],
    road_joints=[],
    road_matrix=[],
    sidewalk_joints=[],
    sidewalk_matrix=[],
    other_dynamic_objects=[
        city.Car(graphics.DEFAULT_SPRITE, (-900, -100), linear_acceleration=100, angular_acceleration=60, mass=5, max_speed=200),
    ]
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
                 [0, 1, 0, 0]],
    sidewalk_joints=[Vector2(0, -100), Vector2(600, -100)],
    sidewalk_matrix=[[0, 1],
                     [1, 0]]
)

editor_new_map = Map(
    buildings=[
        Blueprints.p2_5x2.get_building(position=(538, 271), rotation=0, height=7),
        Blueprints.p1_5x2.get_building(position=(734, 771), rotation=90, height=5),
    ],
    road_joints=[Vector2(1400, -100), Vector2(550, 1050), Vector2(-900, 1050), Vector2(-900, -100)],
    road_matrix=[
                 [0, 0, 0, 2],
                 [0, 0, 1, 0],
                 [0, 1, 0, 1],
                 [2, 0, 1, 0],
                ],
    sidewalk_joints=[Vector2(50, 50), Vector2(950, 50), Vector2(950, 950), Vector2(50, 950), ],
    sidewalk_matrix=[
                 [0, 1, 0, 1],
                 [1, 0, 1, 0],
                 [0, 1, 0, 0],
                 [1, 0, 0, 0],
                ],
    other_dynamic_objects=[
        Blueprints.tt_1.get_car(position=(-900, -100)),
        Blueprints.tt_1.get_car(position=(-900, -1050))
    ]
)
