from manim import *
import numpy as np

class LightScaffold(ThreeDScene):
    def construct(self):
        self.camera.background_color = "Black"
        self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES)

        n_rods = 5
        base_length = 4.0

        rods = []
        pulses = []

        for _ in range(n_rods):
            p0 = np.random.uniform(-3, 3, 3)
            direction = np.random.normal(0, 1, 3)
            direction /= np.linalg.norm(direction)
            p1 = p0 + direction * base_length

            base = Line3D(start=p0, end=p1, thickness=0.03, color=GREY_B)

            mid_glow = Line3D(start=p0, end=p1, thickness=0.08, color=TEAL_A)
            mid_glow.set_opacity(0.5)

            outer_glow = Line3D(start=p0, end=p1, thickness=0.16, color=TEAL_A)
            outer_glow.set_opacity(0.2)

            rod_group = VGroup(base, mid_glow, outer_glow)
            rods.append(rod_group)
            self.add(rod_group)

            pulse = Line3D(
                start=p0,
                end=p0,
                thickness=0.16,
                color=TEAL_C
            )
            pulse.set_opacity(1.0)

            pulses.append((pulse, p0, p1))
            self.add(pulse)

        def pulse_updater(pulse_tuple, dt):
            pulse, start, end = pulse_tuple
            direction = end - start
            t = (self.time % 1.0)
            pos = start + t * direction
            w = 0.25
            pulse.put_start_and_end_on(pos - w * direction, pos + w * direction)

        for p in pulses:
            p[0].add_updater(lambda mob, dt, p=p: pulse_updater(p, dt))

        def camera_motion(mob, dt):
            mob.theta += 0.03 * dt

        self.camera.add_updater(camera_motion)

        self.wait(12)
