from manim import *
import numpy as np

class WaveToTorus(ThreeDScene):
    def construct(self):

        ##################################################################
        # 1. PARAMETERS
        ##################################################################
        N = 32                # grid resolution
        spacing = 0.3
        n_points = N * N      # must equal number of torus rings

        # Kelvin wave parameters
        A = 0.4
        k = 3.0
        damping = 0.20
        omega = 2.0

        # Torus parameters
        tube_radius = 0.4
        big_radius  = 2.0


        ##################################################################
        # 2. BUILD THE WAVE GRID (2D circles acting as 3D points)
        ##################################################################
        base_dot = Circle(radius=0.05, color=BLUE)
        grid = VGroup()
        positions = []

        for i in range(N):
            for j in range(N):
                x = (i - N/2) * spacing
                y = (j - N/2) * spacing
                z = 0
                positions.append((x, y))

                dot = base_dot.copy().move_to([x, y, z])
                grid.add(dot)

        self.set_camera_orientation(phi=60*DEGREES, theta=45*DEGREES)
        self.play(FadeIn(grid, run_time=1))


        ##################################################################
        # 3. ADD THE KELVIN WAVE ANIMATION
        ##################################################################
        def update_wave(mob, dt):
            t = self.time
            for dot, (x, y) in zip(mob, positions):
                r = np.sqrt(x*x + y*y)
                phase = k*r - omega*t
                z = A * np.sin(phase) * np.exp(-damping*r)
                dot.move_to([x, y, z])

        grid.add_updater(update_wave)
        self.wait(3)

        grid.remove_updater(update_wave)


        ##################################################################
        # 4. BUILD THE TARGET TORUS WITH EXACTLY N*N RINGS
        ##################################################################
        torus = VGroup()

        base_ring = Circle(radius=tube_radius, color=BLUE)
        base_ring.rotate(PI/2, axis=RIGHT)
        base_ring.shift(RIGHT * big_radius)

        # We will place N*N rings around the torus surface
        # Using a double parameterization in theta and phi

        for idx in range(n_points):
            theta = TAU * (idx % N) / N        # around the big circle
            phi   = TAU * (idx // N) / N       # around the tube

            ring = base_ring.copy()

            # Stretching of the tube (optional)
            stretch_factor = 1 + np.sin(theta) * 0.4
            ring.scale([stretch_factor, 1, stretch_factor], about_point=ring.get_center())

            # Rotate around z-axis for theta
            ring.rotate(theta, axis=OUT, about_point=ORIGIN)

            # Now rotate around the ring’s own center for phi
            ring.rotate(phi, axis=RIGHT, about_point=ring.get_center())

            torus.add(ring)


        ##################################################################
        # 5. MORPH WAVE GRID → TORUS
        ##################################################################
        # Both have 4096 submobjects: safe transform
        self.play(Transform(grid, torus, run_time=4))
        self.wait(1)

        ##################################################################
        # 6. OPTIONAL: ROTATE THE TORUS
        ##################################################################
        self.play(Rotate(grid, angle=TAU, axis=OUT, run_time=6))
        self.wait()
