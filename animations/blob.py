from manim import *

class SplineBlob(Scene):
    def construct(self):

        # ------------------------------------------------------
        # Helper: create a smooth spline blob from anchor points
        # ------------------------------------------------------
        def blob(points, color=RED):
            return VMobject(
                stroke_width=0,
                fill_color=color,
                fill_opacity=1
            ).set_points_smoothly(points)

        # ------------------------------------------------------
        # Define four polynomial-like spline shapes
        # (These are just examples; adjust points for your shapes)
        # ------------------------------------------------------
        blob_A = blob([
            [-3.5, -3.5, 0],
            [-2.8, -1.5, 0],
            [-1.5, -0.5, 0],
            [-0.4, -0.2, 0],
            [-0.2, -1.4, 0],
            [-1.8, -2.8, 0],
            [-3.5, -3.5, 0],
        ])

        blob_B = blob([
            [3.5, -3.5, 0],
            [2.0, -1.4, 0],
            [1.0, -0.5, 0],
            [0.2, -0.3, 0],
            [0.3, -1.8, 0],
            [1.8, -3.0, 0],
            [3.5, -3.5, 0],
        ])

        blob_C = blob([
            [3.5, 3.5, 0],
            [2.0, 2.0, 0],
            [1.2, 1.1, 0],
            [0.3, 0.4, 0],
            [0.2, 1.5, 0],
            [2.0, 3.0, 0],
            [3.5, 3.5, 0],
        ])

        blob_D = blob([
            [-3.5, 3.5, 0],
            [-2.2, 2.0, 0],
            [-1.0, 1.0, 0],
            [-0.3, 0.4, 0],
            [-0.5, 1.6, 0],
            [-2.4, 3.2, 0],
            [-3.5, 3.5, 0],
        ])

        # ------------------------------------------------------
        # Start with blob_A in lower left
        # ------------------------------------------------------
        current = blob_A.copy()
        self.add(current)

        # ------------------------------------------------------
        # Transform through the sequence
        # ------------------------------------------------------
        self.play(Transform(current, blob_B), run_time=2)
        self.play(Transform(current, blob_C), run_time=2)
        self.play(Transform(current, blob_D), run_time=2)
        self.play(Transform(current, blob_A), run_time=2)

        self.wait()
