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


class Camera:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Camera, cls).__new__(cls)
        return cls.instance

    def __init__(self,
                 position: tuple | list | Point2 | Vector2 = Vector2(0, 0),
                 shape: tuple | list | Point2 | Vector2 = Vector2(0, 0),
                 simplified: bool = False):
        self.position: Vector2 = Vector2(*position)

        self.shape: Vector2 = Vector2(*shape)

        self.simplified: bool = simplified
        self.simplified_scale: float = 1

    def zoom(self, zoom_value: float):
        self.position -= 0.5 * ((1 / (self.simplified_scale * zoom_value) * self.shape) - (1 / self.simplified_scale * self.shape))
        self.simplified_scale *= zoom_value

    def zoom_in(self, zoom_value: float):
        self.zoom(zoom_value)

    def zoom_out(self, zoom_value: float):
        self.zoom(1 / zoom_value)

    def get_center_position(self):
        return self.position + 0.5 * self.shape

    def get_relative_position(self, global_position: Vector2):
        if self.simplified:
            return self.simplified_scale * (global_position - self.position)
        return global_position - self.position

    def get_global_position(self, relative_position: Vector2):
        if self.simplified:
            return 1 / self.simplified_scale * relative_position + self.position
        return relative_position + self.position


class Game:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Game, cls).__new__(cls)
        return cls.instance

    def __init__(self, window: Window, city_map: maps.Map, framerate=settings.framerate, input_handling='DEFAULT'):
        self.window = window
        self.camera = Camera(position=[0, 0], shape=self.window.shape)

        self.time = igtime.Time()
        self.framerate = framerate

        self.selection: Object = None
        self.input_handler: callable
        match input_handling:
            case 'DEFAULT':
                self.input_handler = self._handle_input_default
            case 'PHYSICS_TEST':
                self.input_handler = self._handle_input_physics

            case _:
                raise 'invalid input handling type: "' + input_handling + '"'

        self.dynamic_objects: list[Object] = []
        self.static_objects: list[Object] = []
        self.objects: list[Object] = city_map.get_objects()
        self.roads: RoadGraph = city_map.get_roads()

        self.shift_x_hold = False

        self.running: bool = True
        self.delta: float = 0

    def update(self):
        input_events = self.window.get_input()
        self.input_handler(input_events)

        if self.camera.simplified:
            self.window.fill(Color.sDEFAULT)
        else:
            self.window.fill(Color.DEFAULT)

        if self.roads:
            self.roads.render_to(self.window, self.camera)

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
                self.camera.simplified = not self.camera.simplified
                self.camera.simplified_scale = 1
                self.shift_x_hold = True

        elif self.shift_x_hold:
            self.shift_x_hold = False

        for event in input_events:
            match event:
                case InputType.W:
                    self.camera.position.y -= settings.camera_speed / self.camera.simplified_scale
                case InputType.A:
                    self.camera.position.x -= settings.camera_speed / self.camera.simplified_scale
                case InputType.S:
                    self.camera.position.y += settings.camera_speed / self.camera.simplified_scale
                case InputType.D:
                    self.camera.position.x += settings.camera_speed / self.camera.simplified_scale

                case InputType.SCROLL_UP:
                    if self.camera.simplified:
                        self.camera.zoom_in(1.05)
                case InputType.SCROLL_DOWN:
                    if self.camera.simplified:
                        self.camera.zoom_out(1.05)

                case InputType.QUIT:
                    self.running = False

    def _handle_input_physics(self, input_events: list):
        for event in input_events:
            match event:
                case InputType.W:
                    self.camera.position.y -= settings.camera_speed / self.camera.simplified_scale
                case InputType.A:
                    self.camera.position.x -= settings.camera_speed / self.camera.simplified_scale
                case InputType.S:
                    self.camera.position.y += settings.camera_speed / self.camera.simplified_scale
                case InputType.D:
                    self.camera.position.x += settings.camera_speed / self.camera.simplified_scale

                case InputType.LMB:
                    new_selection = self._get_selected(self.window.get_mouse_position())
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

    def _get_selected(self, click: Vector2):
        global_click = self.camera.get_global_position(click)

        for obj in self.objects:
            if hasattr(obj, 'radius'):
                if obj.position.dist(global_click.x, global_click.y) <= obj.radius:
                    return obj

            elif hasattr(obj, 'rect'):
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
