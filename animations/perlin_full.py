from manim import *
import numpy as np


class PerlinMesh(ThreeDScene):
    def construct(self):

        self.set_camera_orientation(phi=65*DEGREES, theta=-45*DEGREES)

        amp = 1.5
        speed = 0.25

        # random offsets for the Perlin-like field
        ox, oy, ot = np.random.rand(3) * 1

        # Gaussian lighting parameters
        z0 = 0.05
        sigma = 0.08

        # -------------------------------------------------------------------
        # Perlin-like smooth height field
        # -------------------------------------------------------------------
        def perlin(x, y, t):
            v  = 0.6*np.sin(0.6*x + 0.6*y + 1.2*t + ox)
            v += 0.3*np.sin(1.1*x - 0.7*y + 1.4*t + oy)
            v += 0.25*np.sin(0.4*x + 1.2*y - 0.8*t + ot)
            return amp * v

        def gaussian(z):
            return np.exp(-((z - z0)**2) / (2*sigma**2))

        # -------------------------------------------------------------------
        # Build a grid of vertices
        # -------------------------------------------------------------------
        N = 60
        xs = np.linspace(-5, 5, N)
        ys = np.linspace(-5, 5, N)

        # Initialize triangles
        triangles = VGroup()

        def build_triangles(t):
            tris = VGroup()
            for i in range(N - 1):
                for j in range(N - 1):
                    x0, x1 = xs[j], xs[j+1]
                    y0, y1 = ys[i], ys[i+1]

                    # heights at 4 corners
                    z00 = perlin(x0, y0, t)
                    z10 = perlin(x1, y0, t)
                    z01 = perlin(x0, y1, t)
                    z11 = perlin(x1, y1, t)

                    # triangle 1
                    tri1 = Polygon(
                        np.array([x0, y0, z00]),
                        np.array([x1, y0, z10]),
                        np.array([x0, y1, z01]),
                        stroke_width=0
                    )

                    # triangle 2
                    tri2 = Polygon(
                        np.array([x1, y0, z10]),
                        np.array([x1, y1, z11]),
                        np.array([x0, y1, z01]),
                        stroke_width=0
                    )

                    # lighting color via gaussian
                    zmean1 = (z00 + z10 + z01) / 3
                    zmean2 = (z10 + z11 + z01) / 3

                    col1 = interpolate_color(BLUE_E, WHITE, gaussian(zmean1))
                    col2 = interpolate_color(BLUE_E, WHITE, gaussian(zmean2))

                    tri1.set_fill(col1, opacity=1)
                    tri2.set_fill(col2, opacity=1)

                    tris.add(tri1, tri2)

            return tris

        # create initial frame
        tris = build_triangles(0)
        self.add(tris)

        # updater: rebuild triangles each frame
        def update_mesh(mob, dt):
            t = self.time * speed
            new_tris = build_triangles(t)
            mob.become(new_tris)

        tris.add_updater(update_mesh)

        self.wait(10)
