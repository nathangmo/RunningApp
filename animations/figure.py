from manim import *
import numpy as np

# Vertical 9:16 output
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16


# --------------------------------------------------------------------------
# Global stroke factory (cleanest for Manim)
# --------------------------------------------------------------------------
def make_arrow_stroke(x, y, length=0.4, angle=0.0):
    dx = length * np.cos(angle)
    dy = length * np.sin(angle)

    main_line = Line(
        [x, y, 0],
        [x + dx, y + dy, 0],
        color=WHITE,
        stroke_width=6
    )

    head_len = 0.12 * length
    head_angle = angle - np.pi / 6

    hx = (x + dx) - head_len * np.cos(head_angle)
    hy = (y + dy) - head_len * np.sin(head_angle)

    head_line = Line(
        [x + dx, y + dy, 0],
        [hx, hy, 0],
        color=WHITE,
        stroke_width=6
    )

    return VGroup(main_line, head_line)


# --------------------------------------------------------------------------
# Boat path
# --------------------------------------------------------------------------
def boat_path(t):
    y = 6 * (1 - t) - 2
    x = 0.0 * np.sin(2.5 * np.pi * t)
    return np.array([x, y, 0])


# --------------------------------------------------------------------------
# Scene
# --------------------------------------------------------------------------
class SimpleWaveField(Scene):
    def construct(self):
        self.camera.background_color = BLUE

        nx = 9
        ny = 16
        spacing_x = 0.8
        spacing_y = 0.8

        waves = []

        for i in range(nx):
            for j in range(ny):
                x = (i - nx / 2) * spacing_x
                y = (j - ny / 2) * spacing_y

                stroke = make_arrow_stroke(x, y)
                waves.append(stroke)

        group = VGroup(*waves)
        self.add(group)

        # Animate the field with a boat-driven disturbance
        self.play(
            UpdateFromAlphaFunc(group, lambda g, alpha: self.update_field(g, alpha)),
            run_time=6,
            rate_func=linear
        )

    def update_field(self, group, alpha):
        t = alpha
        boat_pos = boat_path(t)

        for stroke in group:
            main_line, head_line = stroke

            xm, ym, _ = main_line.get_center()

            base_angle = 0.25 * np.sin(1.2 * xm + 0.8 * ym + 3 * t)
            base_mag = 0.20

            dx = xm - boat_pos[0]
            dy = ym - boat_pos[1]
            dist = np.sqrt(dx * dx + dy * dy)

            disturbance = np.exp(-(dist ** 2) * 0.6)
            push_angle = np.arctan2(dy, dx)
            push_strength = 0.8 * disturbance

            angle = base_angle + push_strength * push_angle
            mag = base_mag + 0.12 * disturbance

            dx2 = mag * np.cos(angle)
            dy2 = mag * np.sin(angle)

            start = np.array([xm - dx2, ym - dy2, 0])
            end = np.array([xm + dx2, ym + dy2, 0])
            main_line.put_start_and_end_on(start, end)

            head_len = 0.12 * mag
            head_angle = angle - np.pi / 6

            hx = end[0] - head_len * np.cos(head_angle)
            hy = end[1] - head_len * np.sin(head_angle)

            head_line.put_start_and_end_on(end, [hx, hy, 0])
