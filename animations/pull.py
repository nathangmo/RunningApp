from manim import *
import numpy as np
import random

class Arch(Scene):
    def construct(self):
        # Main large arch
        arch_radius = 3.5
        arch = Arc(radius=arch_radius, angle=PI)
        self.add(arch)

        # Helper to compute arc point and tangent unit vector at angle theta
        def arc_point(theta: float) -> np.ndarray:
            return np.array([arch_radius * np.cos(theta), arch_radius * np.sin(theta), 0.0])

        def tangent_unit(theta: float) -> np.ndarray:
            # derivative of (r cos t, r sin t) is r * (-sin t, cos t)
            t = np.array([-np.sin(theta), np.cos(theta), 0.0])
            n = np.linalg.norm(t)
            return t / (n if n != 0 else 1)

        def quadratic_bezier(P0: np.ndarray, P1: np.ndarray, P2: np.ndarray, color=WHITE) -> ParametricFunction:
            # B(u) = (1-u)^2 P0 + 2(1-u)u P1 + u^2 P2, u in [0,1]
            return ParametricFunction(lambda u: (1 - u) ** 2 * P0 + 2 * (1 - u) * u * P1 + u ** 2 * P2,
                                      t_range=[0, 1], stroke_color=color, stroke_width=3)

        # Starting y for all path starts (below the arc)
        start_y = -arch_radius - 1.0

        # Create multiple paths across the arc. Ensure endpoints at 0 and PI are straight vertical lines.
        num_paths = 9
        angles = np.linspace(0, PI, num_paths)

        for theta in angles:
            P2 = arc_point(theta)
            P0 = np.array([P2[0], start_y, 0.0])

            # Make the exact endpoints straight lines (no curvature)
            if np.isclose(theta, 0.0) or np.isclose(theta, PI):
                path = Line(P0, P2, stroke_width=3, color=BLUE)
            else:
                # Place control point along the arc tangent so the bezier meets the arc tangentially.
                # P1 = P2 - k * t_hat where k controls how sharply the curve meets the arc.
                t_hat = tangent_unit(theta)
                # smaller k -> gentler curve; scale k by angle distance from endpoints for variety
                k = 0.9
                P1 = P2 - k * t_hat
                path = quadratic_bezier(P0, P1, P2, color=BLUE)

            self.add(path)


