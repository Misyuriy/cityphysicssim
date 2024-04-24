import graphics
from graphics import Sprite, Window, InputType

import settings
from settings import Color

from physics import Vector2


class TextButton:
    def __init__(self,
                 text: str,
                 font,
                 position: Vector2,
                 shape: Vector2,
                 text_color: tuple,
                 button_normal_color: tuple,
                 button_pressed_color: tuple = None,
                 button_hover_color: tuple = None
                 ):
        self.text: str = text
        self.font = font

        self.position: Vector2 = position
        self.shape: Vector2 = shape

        self.state = 0

        self.text_color: tuple = text_color
        self.button_state_colors: list = [
            button_normal_color,
            button_pressed_color if button_pressed_color else button_normal_color,
            button_hover_color if button_hover_color else button_normal_color,
        ]

    def render_to(self, window: Window):
        text_shape = Vector2(*self.font.size(self.text))
        text_edge_position = self.position + 0.5 * (self.shape - text_shape)

        window.render_rect(self.position, self.shape, self.button_state_colors[self.state])
        window.draw_text_label(self.text, self.text_color, text_edge_position, font_option='subtitle')

    def update(self, input_events: list, mouse_position: Vector2):
        br_corner = self.position + self.shape

        released = False

        if self.position.x <= mouse_position.x <= br_corner.x and self.position.y <= mouse_position.y <= br_corner.y:
            if InputType.LMB in input_events:
                self.state = 1
            else:
                if self.state == 1:
                    released = True
                self.state = 2
        else:
            if self.state == 1:
                released = True
            self.state = 0

        return released


class UI:
    class State:
        def __init__(self, text_labels: list, buttons: list[TextButton]):
            self.text_labels = text_labels
            self.buttons = buttons

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(UI, cls).__new__(cls)
        return cls.instance

    def __init__(self, window: Window, state_key: str = 'MAIN_MENU'):
        self.states: dict[str, UI.State] = {
            'MAIN_MENU': UI.State(
                text_labels=[
                    ('CITY PLANNER PY', Color.WHITE, Vector2(96, 64), 'title')
                ],
                buttons=[
                    TextButton('Simulate city',
                               window.fonts['subtitle'],
                               Vector2(141, 200), Vector2(320, 64),
                               Color.WHITE,
                               Color.uiDEFAULT,
                               button_pressed_color=Color.uiPRESSED,
                               button_hover_color=Color.uiHOVER),
                    TextButton('Edit city',
                               window.fonts['subtitle'],
                               Vector2(141, 264), Vector2(320, 64),
                               Color.WHITE,
                               Color.uiDEFAULT,
                               button_pressed_color=Color.uiPRESSED,
                               button_hover_color=Color.uiHOVER),
                    TextButton('Quit',
                               window.fonts['subtitle'],
                               Vector2(141, 392), Vector2(320, 64),
                               Color.WHITE,
                               Color.uiDEFAULT_RED,
                               button_pressed_color=Color.uiPRESSED_RED,
                               button_hover_color=Color.uiHOVER_RED),
                ]
            ),
            'MAP_EDITOR': UI.State(
                text_labels=[
                    ('TEST UI', Color.WHITE, Vector2(20, 0), 'title'),
                    ('On Windows pygame.font.get_fonts() returns large number of system fonts', Color.WHITE, Vector2(20, 80), 'text')
                ],
                buttons=[
                    TextButton('BUTTON',
                               window.fonts['subtitle'],
                               Vector2(20, 120), Vector2(200, 100),
                               Color.WHITE,
                               Color.RED,
                               button_pressed_color=Color.BLACK,
                               button_hover_color=Color.BLUE)
                ]
            ),
            'DEFAULT': UI.State(
                text_labels=[
                    ('TEST UI', Color.WHITE, Vector2(20, 0), 'title'),
                    ('On Windows pygame.font.get_fonts() returns large number of system fonts', Color.WHITE,
                     Vector2(20, 80), 'text')
                ],
                buttons=[
                    TextButton('BUTTON',
                               window.fonts['subtitle'],
                               Vector2(20, 120), Vector2(200, 100),
                               Color.WHITE,
                               Color.RED,
                               button_pressed_color=Color.BLACK,
                               button_hover_color=Color.BLUE)
                ]
            )
        }

        self.state = self.states[state_key]

    def set_state(self, state_key: str):
        if state_key not in self.states.keys():
            raise 'invalid UI state key: "' + state_key + '"'

        self.state = self.states[state_key]

    def render_to(self, window: Window):
        for button in self.state.buttons:
            button.render_to(window)

        for label_parameters in self.state.text_labels:
            window.draw_text_label(
                label_parameters[0],
                label_parameters[1],
                label_parameters[2],
                font_option=label_parameters[3]
            )

    def update(self, input_events: list, mouse_position: Vector2):
        button_signals = {}
        for button in self.state.buttons:
            signal = button.update(input_events, mouse_position)
            button_signals[button.text] = signal

        return button_signals
