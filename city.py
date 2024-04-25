import random

import graphics
from graphics import Sprite

import physics
from physics import Point2, Vector2, Object

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

        self.distance_matrix: list[list] = [[0 for _ in range(self.n_joints)] for _ in range(self.n_joints)]
        self.recalculate_distance_matrix()

        self.s_joint_color: tuple
        self.s_road_color: tuple
        self.road_color: tuple
        self.road_size: int

        match color_variant:
            case 0:
                self.s_joint_color = Color.sVERTEX
                self.s_road_color = Color.sROAD
                self.road_color = Color.DARK_ASPHALT
                self.road_size = settings.road_size

            case 1:
                self.s_joint_color = Color.sSIDEWALK_VERTEX
                self.s_road_color = Color.sSIDEWALK
                self.road_color = Color.ASPHALT
                self.road_size = settings.sidewalk_size

            case _:
                raise 'invalid color variant for RoadGraph: ' + str(color_variant)

    def recalculate_distance_matrix(self):
        self.distance_matrix = [[0 for _ in range(self.n_joints)] for _ in range(self.n_joints)]

        for i, joint1 in enumerate(self.joints):
            for j, joint2 in enumerate(self.joints):
                self.distance_matrix[i][j] = joint1.dist(joint2.x, joint2.y)

    def get_joint_radius(self, index: int):
        max_roads = max(self.matrix[index])
        return self.road_size * max_roads

    def get_closest_joint_to(self, position: Vector2):
        min_distance = float('inf')
        closest_joint = None

        for index, joint in enumerate(self.joints):
            if joint.dist(position.x, position.y) < min_distance:
                min_distance = joint.dist(position.x, position.y)
                closest_joint = index

        return closest_joint

    def get_neighbors_of(self, index: int):
        connections = []
        for j in range(self.n_joints):
            if self.matrix[index][j] != 0:
                connections.append(j)

        return connections

    def get_shortest_path(self, start_index: int, end_index: int):
        # Dijkstra algorithm

        unvisited_indexes = list(range(self.n_joints))
        path_lengths = [float('inf') for _ in range(self.n_joints)]
        previous_joints = [-1 for _ in range(self.n_joints)]

        path_lengths[start_index] = 0

        while unvisited_indexes:
            current_min_index = None
            for index in unvisited_indexes:
                if current_min_index is None:
                    current_min_index = index
                elif path_lengths[index] < path_lengths[current_min_index]:
                    current_min_index = index

            neighbors = self.get_neighbors_of(current_min_index)
            for neighbor in neighbors:
                tentative_value = path_lengths[current_min_index] + self.distance_matrix[current_min_index][neighbor]
                if tentative_value < path_lengths[neighbor]:
                    path_lengths[neighbor] = tentative_value

                    previous_joints[neighbor] = current_min_index

            unvisited_indexes.pop(unvisited_indexes.index(current_min_index))

        path = []
        index = end_index

        while index != start_index:
            path.append(index)
            index = previous_joints[index]

        path.append(start_index)

        return path

    def add_joint(self, position: Vector2, connected_index: int, connection_to_new: int = 1, connection_from_new: int = 1):
        self.joints.append(position)
        self.n_joints += 1

        self.matrix = [i + [0] for i in self.matrix]
        self.matrix.append([0] * self.n_joints)

        self.matrix[connected_index][-1] = connection_to_new
        self.matrix[-1][connected_index] = connection_from_new

        self.recalculate_distance_matrix()

    def set_joint_position(self, index: int, new_position: Vector2):
        self.joints[index] = new_position
        self.recalculate_distance_matrix()

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

                window.render_circle(camera.schematic_scale * self.road_size * max_roads,
                                     camera.get_relative_position(joint), color)
            else:
                window.render_circle(self.road_size * max_roads, camera.get_relative_position(joint), self.road_color)

    def render_road_to(self, window: graphics.Window, camera, i: int, j: int):
        relative_position = camera.get_relative_position(Vector2(0, 0))

        if camera.schematic:
            color = self.s_road_color
            if [i, j] == self.selected_road or [j, i] == self.selected_road:
                color = Color.sSELECTED
            window.render_line(relative_position + (camera.schematic_scale * self.joints[i]),
                               relative_position + (camera.schematic_scale * self.joints[j]),
                               width=camera.schematic_scale * self.road_size * (
                                           self.matrix[i][j] + self.matrix[j][i]),
                               color=color)
            return

        window.render_line(relative_position + self.joints[i],
                           relative_position + self.joints[j],
                           width=self.road_size * (self.matrix[i][j] + self.matrix[j][i]),
                           color=self.road_color)
        if self.road_color == Color.ASPHALT:
            return

        window.render_line_edges(relative_position + self.joints[i],
                                 relative_position + self.joints[j],
                                 width=self.road_size * (self.matrix[i][j] + self.matrix[j][i]),
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
                                             width=self.road_size * n_roads,
                                             color=Color.MARKING_WHITE,
                                             edge_width=settings.marking_size,
                                             dash=settings.dotted_marking[0],
                                             gap=settings.dotted_marking[1])


class Car(physics.PhysicsRectAgent):
    def __init__(self,
                 sprite: Sprite,
                 position: tuple | list | Point2 | Vector2,
                 rotation: float = 0,
                 linear_acceleration: float = 0,
                 angular_acceleration: float = 0,
                 name: str = 'Car',
                 radius: float = None,
                 mass: float = 1,
                 max_speed: float = 0,
                 turning_margin: float = 0.5,
                 crashed_sprite: Sprite = None,
                 schematic_color: tuple | list = Color.sCAR
                 ):
        super().__init__(sprite, position, rotation, linear_acceleration, angular_acceleration, name, radius, mass, schematic_color)
        self.max_speed: float = max_speed
        self.allowed_speed: float = max_speed

        self.previous_vertex: Vector2 = self.position
        self.path: list[Vector2] = []
        self.path_min_distance: float = settings.path_min_distance
        self.turning_margin = turning_margin

        self.crashed_sprite = crashed_sprite

    def update(self, delta, collisions: list[Object] = None):
        if self.active:
            if self.path and self.position.dist(self.path[0].x, self.path[0].y) <= self.path_min_distance:
                self.previous_vertex = self.path.pop(0)

            #if self.path:
            #    road_vector = self.path[0] - self.previous_vertex

            if not self.path:
                self.desired_velocity = Vector2(0, 0)
            else:
                self.desired_velocity = self.path[0] - self.position
                added_velocities = 1

                while added_velocities < len(self.path):
                    next_desired_velocity = self.path[added_velocities] - self.position

                    if abs(self.desired_velocity.normalize() - next_desired_velocity.normalize()) < settings.min_next_desired_difference:
                        self.desired_velocity += next_desired_velocity
                        added_velocities += 1
                    else:
                        break

            if abs(self.desired_velocity) > self.allowed_speed:
                self.desired_velocity = self.allowed_speed * self.desired_velocity.normalize()

        super().update(delta, collisions)

    def set_allowed_speed(self, new_allowed_speed: float):
        if new_allowed_speed > self.max_speed:
            self.allowed_speed = self.max_speed
        else:
            self.allowed_speed = new_allowed_speed

    def set_path(self, new_path: list[Vector2]):
        self.path = new_path

    def crash(self):
        self.active = False
        self.linear_velocity = Vector2(0, 0)
        self.angular_velocity = 0

        if self.crashed_sprite:
            self.sprite = self.crashed_sprite

    def render_to(self, window, camera):
        super().render_to(window, camera)

        if self.render_velocities:
            start = camera.get_relative_position(self.previous_vertex)

            if self.path:
                for vertex in self.path:
                    end = camera.get_relative_position(vertex)
                    window.render_line(start, end, color=Color.BLUE)
                    window.render_circle(self.path_min_distance * camera.schematic_scale, end, color=Color.BLUE)

                    start = end


class CityPathfinding:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CityPathfinding, cls).__new__(cls)
        return cls.instance

    def __init__(self,
                 agents: list[Object],
                 obstacles: list[Object],
                 roads: RoadGraph,
                 sidewalks: RoadGraph,
                 car_blueprints: list = []):
        self.agents: list[Object] = agents
        self.obstacles: list[Object] = obstacles
        self.objects: list[Object] = self.agents + self.obstacles

        self.roads: RoadGraph = roads
        self.sidewalks: RoadGraph = sidewalks

        self.car_blueprints = car_blueprints

    def update(self, delta: float):
        for agent in self.agents:
            if (not agent.path) and agent.active:
                if isinstance(agent, Car):
                    self._set_agent_random_path(agent, self.roads)

            agent.update(delta)

        for obj in self.objects:
            for obj2 in self.objects:
                if (obj != obj2) and obj.is_colliding_with(obj2):
                    if hasattr(obj, 'active'):
                        obj.crash()

                    if hasattr(obj2, 'active'):
                        obj2.crash()

    def spawn_agents(self, density: float = 1) -> list:
        if not self.car_blueprints:
            return []

        new_agents = []
        for joint in self.roads.joints:
            if random.uniform(0, 1) <= density: # if density = 1 or more, cars will spawn at all joints
                blueprint_choice = random.choice(self.car_blueprints)

                car = blueprint_choice.get_car(position=joint)
                new_agents.append(car)

        self.objects += new_agents
        self.agents += new_agents

        return new_agents

    def clear_agents(self):
        self.agents.clear()

    def _set_agent_random_path(self, agent: Object, graph: RoadGraph):
        closest = graph.get_closest_joint_to(agent.position)
        target = random.randint(0, graph.n_joints - 1)

        index_path = graph.get_shortest_path(closest, target)
        path = []

        for i in range(len(index_path) - 1):
            index = index_path[i]
            next_index = index_path[i + 1]

            road_vector = graph.joints[next_index] - graph.joints[index]
            lane_vector = settings.road_size * road_vector.normalize().rotate(-90)

            selected_lane = random.randint(0, graph.matrix[index][next_index] - 1)

            path.append(graph.joints[index] + (0.5 + selected_lane) * lane_vector)

            intermediate_x = settings.path_intermediate_points_distance
            while intermediate_x < abs(road_vector):
                intermediate_road_vector = intermediate_x * road_vector.normalize()
                path.append(graph.joints[index] + intermediate_road_vector + (0.5 + selected_lane) * lane_vector)

                intermediate_x += settings.path_intermediate_points_distance

            path.append(graph.joints[next_index] + (0.5 + selected_lane) * lane_vector)

        path.reverse()

        agent.set_path(path)
