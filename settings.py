framerate = 60
print_map_on_quit = True

# ___ Rendering and UI ____________________________
render_hitbox = False
render_velocities = False

camera_speed = 200
camera_zoom_speed = 1.05

parallax_scaling_step = 1.05
parallax_moving_step = 1 / 16

map_grids = [(100, 100, 5, 0.1), (500, 500, 5, 0.2), (1000, 1000, 5, 0.4)] # (step_x, step_y, width, color_intensiveness)


class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)

    DEFAULT = (200, 200, 255)

    GRASS = (113, 135, 90)
    DIRT = (125, 105, 90)
    ASPHALT = (104, 104, 98)
    DARK_ASPHALT = (55, 55, 53)
    MARKING_WHITE = (222, 222, 206)

    sDEFAULT = (96, 156, 186)
    sGRID = (255, 255, 255)

    sSIDEWALK = (226, 226, 189)
    sSIDEWALK_VERTEX = (245, 245, 229)
    sBUILDING = (189, 212, 226)
    sCAR = (174, 221, 174)
    sROAD = (226, 189, 189)
    sVERTEX = (245, 229, 229)

    sSELECTED = (189, 226, 212)

    uiDEFAULT = (160, 195, 214)
    uiPRESSED = (96, 156, 186)
    uiHOVER = (189, 212, 226)

    uiDEFAULT_RED = (214, 160, 160)
    uiPRESSED_RED = (186, 96, 96)
    uiHOVER_RED = (226, 189, 189)


# ___ City ____________________________
road_size = 80
sidewalk_size = 48

marking_size = 4
dotted_marking = [48, 48]

car_spawn_density = 0.5


# ___ Physics ______________________________
linear_mu = 1
angular_mu = 1


# ___ Pathfinding __________________________
path_min_distance = 128
