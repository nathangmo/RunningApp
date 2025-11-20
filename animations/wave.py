from manim import *
import numpy as np

# Vertical 9:16 output
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9
config.frame_height = 16


class SimpleWaveField(Scene):
    def construct(self):
        self.camera.background_color = "#35a9e0"  # light water blue

        nx = 18
        ny = 32
        spacing_x = 0.4
        spacing_y = 0.4

        waves = []

        for i in range(nx):
            for j in range(ny):
                x = (i - nx / 2) * spacing_x
                y = (j - ny / 2) * spacing_y

                L = Line(
                    start=[x - 0.15, y, 0],
                    end=[x + 0.15, y, 0],
                    color=WHITE,
                    stroke_width=6
                )
                waves.append(L)

        group = VGroup(*waves)
        self.add(group)

        self.play(
            UpdateFromAlphaFunc(group, lambda g, alpha: self.update_field(g, alpha)),
            run_time=6,
            rate_func=linear
        )

    def update_field(self, group, alpha):
        # Time for base flow
        t = alpha * 6.0

        # Boat position: moves straight down along x = 0
        # Grid y runs about [-6.4, 6.0], so start a bit above and end a bit below
        boat_y = 7.0 - 14.0 * alpha

        # Kelvin-like parameters
        theta_deg = 25.0          # half-angle of V (Kelvin is ~19.5°, this is a bit wider)
        k = np.tan(np.deg2rad(theta_deg))

        sigma_x = 0.6             # lateral width of each arm
        L_decay = 20.0             # decay of wake strength with distance behind boat
        omega = 4.0               # frequency of crests along the arm
        A = 1.0                   # rotation amplitude contributed by wake

        for L in group:
            start = L.get_start()
            end = L.get_end()

            xm = 0.5 * (start[0] + end[0])
            ym = 0.5 * (start[1] + end[1])

            # Base smooth water motion (your original field)
            base_angle = 0.3 * np.sin(1.2 * xm + 0.8 * ym + t)

            # Distance behind boat
            s = ym - boat_y

            wake_angle = 0.0
            if s > 0:  # only behind the boat

                # Lateral offset
                x = xm

                # Distance to each ray x = ±k s
                # Left arm
                d_left = x + k * s
                # Right arm
                d_right = x - k * s

                # Gaussian localisation around each arm
                w_left = np.exp(-(d_left ** 2) / (2 * sigma_x ** 2))
                w_right = np.exp(-(d_right ** 2) / (2 * sigma_x ** 2))

                # Overall strength decays with distance behind boat
                axial_decay = np.exp(-s / L_decay)

                # Wave crests along the rays
                crest = np.sin(omega * s)

                # Combined wake amplitude at this point
                amp = A * (w_left + w_right) * axial_decay * crest

                # Sign of rotation: push water outward from centerline
                side_sign = np.sign(x) if x != 0 else 0.0

                wake_angle = side_sign * amp

            total_angle = base_angle + wake_angle

            half_len = 0.15
            dx = half_len * np.cos(total_angle)
            dy = half_len * np.sin(total_angle)

            L.put_start_and_end_on(
                [xm - dx, ym - dy, 0],
                [xm + dx, ym + dy, 0]
            )
