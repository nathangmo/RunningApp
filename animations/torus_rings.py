from manim import *

class TorusRings(ThreeDScene):
    def construct(self):
        tube_radius = 0.4
        big_radius  = 2.0
        n_rings     = 24
        stretch_per_ring = 0.4      # adjust this factor
        # 1. Circle in the x–z plane
        # A default Circle lies in the xy-plane, so we rotate it 90 degrees about the x-axis.
        base = Circle(radius=tube_radius, color=BLUE)
        base.rotate(PI/2, axis=RIGHT)     # xy → xz plane (normal becomes +y)

        # 2. Offset away from the z-axis (to x = big_radius)
        base.shift(RIGHT * big_radius)

        # 3. Duplicate by rotating around the z-axis
        rings = VGroup()
        for k in range(n_rings):
            theta = TAU * k / n_rings
            ring = base.copy()
            stretch_factor = 1 + np.sin(theta) * stretch_per_ring
            ring.scale([stretch_factor, 1, stretch_factor], about_point=ring.get_center())
            ring.rotate(theta, axis=OUT, about_point=ORIGIN)   # rotate around z-axis
            rings.add(ring)

        self.set_camera_orientation(phi=55*DEGREES, theta=45*DEGREES, kappa=20*DEGREES)
        self.play(Create(rings))
        self.play(Rotate(rings, angle=TAU, axis=OUT, run_time=6))
        self.wait()
