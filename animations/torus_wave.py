from manim import *

config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width  = 9
config.frame_height = 16


class TorusBasic(ThreeDScene):
    def construct(self):

        # Camera for 3D
        self.set_camera_orientation(
            phi=60*DEGREES,
            theta=35*DEGREES
        )
        self.renderer.camera.zoom_factor = 1.4

        self.camera.background_color = "#06243f"

        # Create a solid torus
        torus = Torus(major_radius=3, minor_radius=1)
        torus.set_fill(color=BLUE_E, opacity=1.0)
        torus.set_stroke(width=0)

        self.add(torus)

        # Rotate it slowly so you can inspect it
        self.play(
            Rotate(torus, angle=TAU, axis=UP),
            run_time=6,
            rate_func=linear
        )
