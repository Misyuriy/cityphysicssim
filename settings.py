framerate = 60

# ___ Rendering ____________________________
render_hitbox = False

camera_speed = 2
camera_zoom_speed = 1.05

parallax_scaling_step = 1.05
parallax_moving_step = 1 / 16

road_size = 48

marking_size = 4
dotted_marking = [48, 48]

map_grids = [(128, 128, 8, 0.2), (256, 256, 8, 0.4), (512, 512, 8, 0.6)] # (step_x, step_y, width, color_intensiveness)


class Color:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)

    DEFAULT = (200, 200, 255)

    ROAD = (100, 100, 100)

    sDEFAULT = (42, 50, 69)
    sGRID = (255, 255, 255)

    sBUILDING = (56, 71, 102)
    sROAD = (85, 110, 167)
    sVERTEX = (134, 155, 201)
    sSELECTED = (109, 190, 185)


# ___ Physics ______________________________
linear_mu = 1
angular_mu = 1
