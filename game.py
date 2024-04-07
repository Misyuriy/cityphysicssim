import graphics
from graphics import Sprite, Window, InputType
import physics
from physics import Vector2, Point2, Object, intersect

import city
from city import Building, RoadGraph

import igtime

import settings
from settings import Color

import maps
from maps import Blueprints, BuildingBlueprint


class Camera:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Camera, cls).__new__(cls)
        return cls.instance

    def __init__(self,
                 position: tuple | list | Point2 | Vector2 = Vector2(0, 0),
                 shape: tuple | list | Point2 | Vector2 = Vector2(0, 0),
                 schematic: bool = False):
        self.position: Vector2 = Vector2(*position)

        self.shape: Vector2 = Vector2(*shape)

        self.schematic: bool = schematic
        self.schematic_scale: float = 1

    def zoom(self, zoom_value: float):
        self.position -= 0.5 * ((1 / (self.schematic_scale * zoom_value) * self.shape) - (1 / self.schematic_scale * self.shape))
        self.schematic_scale *= zoom_value

    def zoom_in(self, zoom_value: float):
        self.zoom(zoom_value)

    def zoom_out(self, zoom_value: float):
        self.zoom(1 / zoom_value)

    def get_center_position(self):
        return self.position + 0.5 * self.shape

    def get_relative_position(self, global_position: Vector2):
        if self.schematic:
            return self.schematic_scale * (global_position - self.position)
        return global_position - self.position

    def get_global_position(self, relative_position: Vector2):
        if self.schematic:
            return 1 / self.schematic_scale * relative_position + self.position
        return relative_position + self.position


class Game:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Game, cls).__new__(cls)
        return cls.instance

    def __init__(self, window: Window, city_map: maps.Map, framerate=settings.framerate, input_handling='DEFAULT'):
        self.window = window
        self.camera = Camera(position=city_map.initial_camera_position, shape=self.window.shape)

        self.time = igtime.Time()
        self.framerate = framerate

        self.selection = None
        self.input_handler: callable
        match input_handling:
            case 'DEFAULT':
                self.input_handler = self._handle_input_default
            case 'PHYSICS_TEST':
                self.input_handler = self._handle_input_physics_test
            case 'MAP_EDITOR':
                self.input_handler = self._handle_input_editor
                self.camera.schematic = True

            case _:
                raise 'invalid input handling type: "' + input_handling + '"'

        self.dynamic_objects: list[Object] = city_map.get_dynamic_objects()
        self.static_objects: list[Object] = city_map.get_static_objects()
        self.objects: list[Object] = city_map.get_objects()
        self.roads: RoadGraph = city_map.get_roads()
        self.sidewalks: RoadGraph = city_map.get_sidewalks()

        self.shift_x_hold = False

        self.running: bool = True
        self.delta: float = 0

    def update(self):
        input_events = self.window.get_input()
        self.input_handler(input_events)

        if self.camera.schematic:
            self.window.fill(Color.sDEFAULT)
        else:
            self.window.fill(Color.GRASS)

        if self.camera.schematic:
            for grid in settings.map_grids:
                intensiveness = grid[3]
                difference = [Color.sGRID[i] - Color.sDEFAULT[i] for i in range(3)]
                difference = [difference[i] * intensiveness for i in range(3)]

                color = [Color.sDEFAULT[i] + difference[i] for i in range(3)]
                self._render_grid(Vector2(grid[0], grid[1]), width=grid[2], color=color)

        self.sidewalks.render_to(self.window, self.camera)
        self.roads.render_to(self.window, self.camera)

        if self.input_handler != self._handle_input_editor:
            for obj in self.dynamic_objects:
                obj.update(self.delta)

        for obj in self.objects:
            obj.render_to(self.window, self.camera)

            for obj2 in self.objects:
                if obj != obj2 and obj.is_colliding_with(obj2):
                    pass # will implement collision response later

        self.window.update()
        self.delta = self.time.tick(self.framerate)

    def _handle_input_default(self, input_events: list):
        if InputType.X in input_events and InputType.SHIFT in input_events:
            if not self.shift_x_hold:
                self.camera.schematic = not self.camera.schematic
                self.camera.zoom_out(self.camera.schematic_scale)
                self.shift_x_hold = True

        elif self.shift_x_hold:
            self.shift_x_hold = False

        for event in input_events:
            camera_speed = settings.camera_speed
            if InputType.SHIFT in input_events:
                camera_speed *= 2

            match event:
                case InputType.W:
                    self.camera.position.y -= camera_speed / self.camera.schematic_scale
                case InputType.A:
                    self.camera.position.x -= camera_speed / self.camera.schematic_scale
                case InputType.S:
                    self.camera.position.y += camera_speed / self.camera.schematic_scale
                case InputType.D:
                    self.camera.position.x += camera_speed / self.camera.schematic_scale

                case InputType.SCROLL_UP:
                    if self.camera.schematic:
                        self.camera.zoom_in(settings.camera_zoom_speed)
                case InputType.SCROLL_DOWN:
                    if self.camera.schematic:
                        self.camera.zoom_out(settings.camera_zoom_speed)

                case InputType.QUIT:
                    self.running = False

    def _handle_input_physics_test(self, input_events: list):
        for event in input_events:
            match event:
                case InputType.W:
                    self.camera.position.y -= settings.camera_speed / self.camera.schematic_scale
                case InputType.A:
                    self.camera.position.x -= settings.camera_speed / self.camera.schematic_scale
                case InputType.S:
                    self.camera.position.y += settings.camera_speed / self.camera.schematic_scale
                case InputType.D:
                    self.camera.position.x += settings.camera_speed / self.camera.schematic_scale

                case InputType.LMB:
                    new_selection = self._get_selected_physics_object(self.window.get_mouse_position())
                    if new_selection:
                        if self.selection:
                            self.selection.render_hitbox = False

                        self.selection = new_selection
                        self.selection.render_hitbox = True

                    elif self.selection:
                        self.selection.render_hitbox = False
                        self.selection = None

                case InputType.RMB:
                    if self.selection:
                        global_click = self.camera.get_global_position(self.window.get_mouse_position())
                        if hasattr(self.selection, 'linear_velocity'):
                            self.selection.apply_force(linear_force=global_click - self.selection.position)
                        else:
                            self.selection.position = global_click

                        self.selection.render_hitbox = False
                        self.selection = None

                case InputType.SCROLL_UP:
                    if self.selection:
                        if hasattr(self.selection, 'angular_velocity'):
                            self.selection.apply_force(angular_force=50)
                        else:
                            self.selection.rotation += 5

                case InputType.SCROLL_DOWN:
                    if self.selection:
                        if hasattr(self.selection, 'angular_velocity'):
                            self.selection.apply_force(angular_force=-50)
                        else:
                            self.selection.rotation -= 5

                case InputType.QUIT:
                    self.running = False

    def _handle_input_editor(self, input_events: list):
        if InputType.X in input_events and InputType.SHIFT in input_events:
            if not self.shift_x_hold:
                self.camera.schematic = not self.camera.schematic
                self.camera.zoom_out(self.camera.schematic_scale)
                self.shift_x_hold = True

        elif self.shift_x_hold:
            self.shift_x_hold = False

        for event in input_events:
            camera_speed = settings.camera_speed
            if InputType.SHIFT in input_events:
                camera_speed *= 2

            match event:
                case InputType.W:
                    self.camera.position.y -= camera_speed / self.camera.schematic_scale
                case InputType.A:
                    self.camera.position.x -= camera_speed / self.camera.schematic_scale
                case InputType.S:
                    self.camera.position.y += camera_speed / self.camera.schematic_scale
                case InputType.D:
                    self.camera.position.x += camera_speed / self.camera.schematic_scale

                case InputType.Z:
                    if InputType.SHIFT in input_events and isinstance(self.selection, int):
                        selected_graph = self._get_selected_graph()

                        selected_graph.add_joint(
                            self.camera.get_global_position(self.window.get_mouse_position()),
                            self.selection
                        )
                        selected_graph.selected_joint = -1
                        self.selection = None

                case InputType.LMB:
                    self.update_selection(input_events)

                case InputType.RMB:
                    global_click = self.camera.get_global_position(self.window.get_mouse_position())
                    if isinstance(self.selection, Object):
                        self.selection.position = global_click
                    elif isinstance(self.selection, int):
                        selected_graph = self._get_selected_graph()
                        selected_graph.joints[self.selection] = Vector2(global_click)

                case InputType.SCROLL_UP:
                    if isinstance(self.selection, Object) and (InputType.CTRL in input_events):
                        if InputType.SHIFT in input_events:
                            self.selection.rotation += 5
                        else:
                            self.selection.rotation += 1

                    else:
                        self.camera.zoom_in(settings.camera_zoom_speed)

                case InputType.SCROLL_DOWN:
                    if isinstance(self.selection, Object) and (InputType.CTRL in input_events):
                        if InputType.SHIFT in input_events:
                            self.selection.rotation -= 5
                        else:
                            self.selection.rotation -= 1

                    else:
                        self.camera.zoom_out(settings.camera_zoom_speed)

                case InputType.K1:
                    if self.selection is not None:
                        continue

                    self.spawn_building(Blueprints.p1_5x2)

                case InputType.K2:
                    self._try_set_selected_road_to(2)
                    if self.selection is not None:
                        continue
                        
                    self.spawn_building(Blueprints.p2_5x2)

                case InputType.K4:
                    self._try_set_selected_road_to(4)

                case InputType.K6:
                    self._try_set_selected_road_to(6)

                case InputType.K8:
                    self._try_set_selected_road_to(8)

                case InputType.DELETE:
                    self._try_set_selected_road_to(0)

                case InputType.QUIT:
                    self.print_map()
                    self.running = False

    def _reset_selection(self):
        if isinstance(self.selection, Object):
            self.selection.schematic_color = self._get_color_for_object(self.selection)
        else:
            self.roads.selected_joint = -1
            self.roads.selected_road = [-1, -1]
            self.sidewalks.selected_joint = -1
            self.sidewalks.selected_road = [-1, -1]
        self.selection = None

    def update_selection(self, input_events: list):
        click = self.window.get_mouse_position()

        new_selection = self._get_selected_physics_object(click)
        new_selected_graph = None

        if new_selection is None:
            new_selected_graph = self.roads
            new_selection = self._get_selected_road_joint(click)

            if new_selection is None:
                new_selected_graph = self.sidewalks
                new_selection = self._get_selected_sidewalk_joint(click)

                if new_selection is None:
                    new_selected_graph = None

        selected_graph = self._get_selected_graph()
        if new_selection is not None:
            if isinstance(self.selection, Object):
                self.selection.schematic_color = self._get_color_for_object(self.selection)

            elif (InputType.SHIFT in input_events) and self.selection != new_selection:
                if selected_graph != new_selected_graph:
                    pass

                elif isinstance(self.selection, int):
                    new_selection = [self.selection, new_selection]

                elif isinstance(self.selection, list) and (new_selection == self.selection[0]):
                    new_selection = [self.selection[1], new_selection]
                elif isinstance(self.selection, list) and (new_selection == self.selection[1]):
                    new_selection = [self.selection[0], new_selection]

                if selected_graph:
                    selected_graph.selected_joint = -1
                    selected_graph.selected_road = [-1, -1]

            elif selected_graph:
                selected_graph.selected_joint = -1
                selected_graph.selected_road = [-1, -1]

            self.selection = new_selection
            if isinstance(self.selection, Object):
                self.selection.schematic_color = Color.sSELECTED
            elif isinstance(self.selection, int):
                new_selected_graph.selected_joint = self.selection
            else:
                new_selected_graph.selected_road = self.selection

        elif self.selection is not None:
            self._reset_selection()

    def spawn_building(self, blueprint: BuildingBlueprint):
        global_mouse_position = self.camera.get_global_position(self.window.get_mouse_position())

        new_building = blueprint.get_building(global_mouse_position, height=5)
        self.static_objects.append(new_building)
        self.objects.append(new_building)

        self.selection = new_building
        new_building.schematic_color = Color.sSELECTED

    def _try_set_selected_road_to(self, width: int):
        if not isinstance(self.selection, list):
            return

        selected_graph = self._get_selected_graph()
        if selected_graph != self.roads:
            return

        i = self.selection[0]
        j = self.selection[1]

        selected_graph.matrix[i][j] = width // 2
        selected_graph.matrix[j][i] = width // 2

    def _render_grid(self, grid_step: Vector2, width: int, color: tuple | list = Color.sGRID):
        x_step = (self.camera.position.x // grid_step.x) * grid_step.x
        x_end = self.camera.position.x + (self.camera.shape.x / self.camera.schematic_scale)

        y_step = (self.camera.position.y // grid_step.y) * grid_step.y
        y_end = self.camera.position.y + (self.camera.shape.y / self.camera.schematic_scale)

        while x_step <= x_end:
            start = self.camera.get_relative_position(Vector2(x_step, self.camera.position.y))
            end = self.camera.get_relative_position(Vector2(x_step, y_end))
            self.window.render_line(start, end, width=width * self.camera.schematic_scale,
                                    color=color)
            x_step += grid_step.x

        while y_step <= y_end:
            start = self.camera.get_relative_position(Vector2(self.camera.position.x, y_step))
            end = self.camera.get_relative_position(Vector2(x_end, y_step))
            self.window.render_line(start, end, width=width * self.camera.schematic_scale,
                                    color=color)
            y_step += grid_step.y

    def _get_selected_physics_object(self, click: Vector2):
        global_click = self.camera.get_global_position(click)

        for obj in self.objects:
            if isinstance(obj, physics.PhysicsDynamicCircle):
                if obj.position.dist(global_click.x, global_click.y) <= obj.radius:
                    return obj

            elif isinstance(obj, physics.PhysicsStaticRect):
                a, b, c, d = obj.get_vertices()
                segments = [(a, b), (b, c), (c, d), (d, a)]

                r1 = global_click
                r2 = obj.position

                selected = True
                for segment in segments:
                    if intersect(r1, r2, segment[0], segment[1]):
                        selected = False

                if selected:
                    return obj

        return None

    def _get_selected_road_joint(self, click: Vector2):
        global_click = self.camera.get_global_position(click)

        for index, joint in enumerate(self.roads.joints):
            radius = self.roads.get_joint_radius(index)
            if joint.dist(global_click.x, global_click.y) <= radius:
                return index

    def _get_selected_sidewalk_joint(self, click: Vector2):
        global_click = self.camera.get_global_position(click)

        for index, joint in enumerate(self.sidewalks.joints):
            radius = self.sidewalks.get_joint_radius(index)
            if joint.dist(global_click.x, global_click.y) <= radius:
                return index

    def _get_selected_graph(self):
        if (self.roads.selected_road != [-1, -1]) or (self.roads.selected_joint != -1):
            return self.roads
        elif (self.sidewalks.selected_road != [-1, -1]) or (self.sidewalks.selected_joint != -1):
            return self.sidewalks
        return None

    def _get_color_for_object(self, obj: Object):
        if isinstance(obj, Building):
            return Color.sBUILDING
        return None

    def print_map(self):
        print('new_map = Map(')
        print('    buildings=[')
        for building in self.objects:
            int_position = Vector2(int(building.position.x), int(building.position.y))
            print(f'        Blueprints.BLUEPRINTNAME.get_building(position={int_position}, rotation={int(building.rotation)}, height={building.height}),')
        print('    ],')

        print('    road_joints=[', end='')
        for joint in self.roads.joints:
            print(f'Vector2{Vector2(int(joint.x), int(joint.y))}, ', end='')
        print('],')

        print('    road_matrix=[')

        for row in self.roads.matrix:
            print(f'                 {row},')
        print('                ],')

        print('    sidewalk_joints=[', end='')
        for joint in self.sidewalks.joints:
            print(f'Vector2{Vector2(int(joint.x), int(joint.y))}, ', end='')
        print('],')

        print('    sidewalk_matrix=[')

        for row in self.sidewalks.matrix:
            print(f'                 {row},')
        print('                ]')

        print(')')
