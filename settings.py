framerate = 60

# ___ Rendering ____________________________
render_hitbox = False

camera_speed = 2

parallax_scaling_step = 1.05
parallax_moving_step = 1 / 16

road_size = 48

marking_size = 4
dotted_marking = [48, 48]


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
    sBUILDING = (56, 71, 102)
    sROAD = (85, 110, 167)
    sVERTEX = (134, 155, 201)


# ___ Physics ______________________________
linear_mu = 1
angular_mu = 1
