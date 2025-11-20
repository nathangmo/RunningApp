from manim import *
import numpy as np


class RandomWaveField(ThreeDScene):
    def construct(self):
        N_x = 10
        N_y = 10
        spacing = 0.3

        A = 0.15
        speed = 0.5
        freq = 0.4

        # Dot field
        dots = VGroup()
        positions = []
        base = Circle(radius=0.015, color=BLUE)

        for i in range(N_x):
            for j in range(N_y):
                x = (i - N_x/2) * spacing
                y = (j - N_y/2) * spacing
                positions.append((x, y))
                dots.add(base.copy().move_to([x, y, 0]))

        # -------------------------------------------------------
        # Sparse grid that lines up with dots
        # -------------------------------------------------------
        step = 2                       # draw every 2nd gridline
        z_grid = -1

        half_x = (N_x/2) * spacing
        half_y = (N_y/2) * spacing

        grid = VGroup()

        # vertical lines aligned with dot columns
        for i in range(0, N_x + 1, step):
            x = (i - N_x/2) * spacing
            grid.add(Line(
                start=[x, -half_y, z_grid],
                end=[x,  half_y, z_grid],
                color=WHITE, stroke_width=1
            ))

        # horizontal lines aligned with dot rows
        for j in range(0, N_y + 1, step):
            y = (j - N_y/2) * spacing
            grid.add(Line(
                start=[-half_x, y, z_grid],
                end=[ half_x, y, z_grid],
                color=WHITE, stroke_width=1
            ))

        # Camera
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)

        # Wave update
        rand_phase = np.random.rand(N_x*N_y) * 10.0

        def update_wave(mob, dt):
            t = self.time * speed
            for idx, (dot, (x, y)) in enumerate(zip(mob, positions)):
                p = rand_phase[idx]
                z = (
                    A * np.sin(freq * (x + p*0.7) + t)
                    + A * 0.7 * np.sin(freq * 0.6 * (y + p*1.1) - t*0.8)
                    + A * 0.4 * np.sin(freq * 0.4 * (x + y + p*1.7) + t*1.3)
                )
                dot.move_to([x, y, z])

        dots.add_updater(update_wave)

        # Show scene
        self.play(FadeIn(grid), FadeIn(dots), run_time=1.0)
        self.wait(12)
