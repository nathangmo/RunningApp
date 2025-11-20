from manim import *
import numpy as np


class PerlinBlanket(ThreeDScene):
    def construct(self):
        N = 40
        spacing = 0.12

        amp = 0.07
        speed = 0.3
        peak_threshold = 0.045
        light_intensity = 7.0

        # Store grid positions
        dots = VGroup()
        positions = []
        base = Circle(radius=0.014, fill_opacity=1, color=BLUE)

        for i in range(N):
            for j in range(N):
                x = (i - N/2) * spacing
                y = (j - N/2) * spacing
                positions.append((x, y))
                dots.add(base.copy().move_to([x, y, 0]))

        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)

        # Pre-generated random offsets for spatial variation
        offsets = np.random.rand(N*N, 3) * 10.0

        # -------------------------------------------------------------
        # Perlin-inspired noise: smooth, layered, coherent
        # -------------------------------------------------------------
        def perlin(x, y, t, ox, oy, ot):
            v = 0.0
            v += np.sin(0.6 * x + 0.6 * y + t + ox) * 0.6
            v += np.sin(1.1 * x - 0.7 * y + 1.4 * t + oy) * 0.3
            v += np.sin(0.4 * x + 1.2 * y - 0.8 * t + ot) * 0.25
            return v

        # -------------------------------------------------------------
        # Frame-by-frame update
        # -------------------------------------------------------------
        def update_surface(mob, dt):
            t = self.time * speed

            for idx, (dot, (x, y)) in enumerate(zip(mob, positions)):
                ox, oy, ot = offsets[idx]

                val = perlin(x, y, t, ox, oy, ot)
                z = amp * val

                dot.move_to([x, y, z])

                # Light up peaks
                if z > peak_threshold:
                    brightness = min(1.0, (z - peak_threshold) * light_intensity)
                    dot.set_fill(interpolate_color(BLUE, WHITE, brightness))
                else:
                    dot.set_fill(BLUE)

        dots.add_updater(update_surface)

        self.play(FadeIn(dots, run_time=1))
        self.wait(15)
