from manim import *
import numpy as np

# Vertical 9:16 output
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16


class SimpleWaveField(Scene):
    def construct(self):
        self.camera.background_color = BLUE

        nx = 18
        ny = 32
        spacing_x = 0.4
        spacing_y = 0.4

        waves = []

        # Create small line strokes
        for i in range(nx):
            for j in range(ny):
                x = (i - nx / 2) * spacing_x
                y = (j - ny / 2) * spacing_y

                # Short horizontal base stroke
                L = Line(
                    start=[x - 0.15, y, 0],
                    end=[x + 0.15, y, 0],
                    color=WHITE,
                    stroke_width=6
                )
                waves.append(L)

        group = VGroup(*waves)
        self.add(group)

        # Animate the field with a "wave pulse" that travels downward
        self.play(
            UpdateFromAlphaFunc(group, lambda g, alpha: self.update_field(g, alpha)),
            run_time=6,
            rate_func=linear
        )

    def update_field(self, group, alpha):
        t = alpha * 6  # seconds

        for L in group:
            start = L.get_start()
            end = L.get_end()

            # Midpoint coordinates
            xm = 0.5 * (start[0] + end[0])
            ym = 0.5 * (start[1] + end[1])

            # Basic undulation
            base_angle = 0.3 * np.sin(1.2 * xm + 0.8 * ym + t)

            # Force pulse traveling downward (ym - vt)
            pulse = np.exp(-((ym - 1.5 * t) ** 2) * 0.8)
            pulse_angle = 1.2 * pulse  # rotation caused by passing force

            total_angle = base_angle + pulse_angle

            # Wave length stays constant
            half_len = 0.15

            dx = half_len * np.cos(total_angle)
            dy = half_len * np.sin(total_angle)

            L.put_start_and_end_on(
                [xm - dx, ym - dy, 0],
                [xm + dx, ym + dy, 0]
            )


