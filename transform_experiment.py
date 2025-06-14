from manim import *

class TransformExperiment(Scene):
    def construct(self):
        square: Square = Square(color = WHITE, fill_color = PURE_BLUE, fill_opacity = 1.0)

        circle: Circle = Circle(color = PURE_RED, fill_color = PURE_GREEN , fill_opacity = 1.0)

        circle.next_to(square, RIGHT, buff=0.5)

        self.play(Create(square)) #, Create(circle))

        # self.play(Create(square), Create(circle))

        # self.wait(0.5)

        # self.play(Transform(square, circle))

        self.play(TransformFromCopy(square, circle))

        # self.play(ReplacementTransform(square, circle))