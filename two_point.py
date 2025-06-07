from manim import *

class TwoPointCrossoverScene(Scene):
    def construct(self):
        # 1. Define parameters
        genome_length = 10
        p1_color = BLUE_C
        p2_color = GREEN_C
        child_fill_color_initial = BLACK
        child_stroke_color_initial = WHITE
        child_fill_opacity_initial = 1.0
        square_buffer = 0.05

        cp1_idx = 2
        cp2_idx = 6

        parent_gene_stroke_color = BLACK
        parent_gene_stroke_width = 2
        parent_gene_fill_opacity = 0.8

        # 2. Create Parent and Child Genome Mobjects
        parent1_genes = VGroup(*[
            Square(side_length=0.7, fill_color=p1_color, fill_opacity=parent_gene_fill_opacity,
                   stroke_color=parent_gene_stroke_color, stroke_width=parent_gene_stroke_width)
            for _ in range(genome_length)
        ]).arrange(RIGHT, buff=square_buffer)

        parent2_genes = VGroup(*[
            Square(side_length=0.7, fill_color=p2_color, fill_opacity=parent_gene_fill_opacity,
                   stroke_color=parent_gene_stroke_color, stroke_width=parent_gene_stroke_width)
            for _ in range(genome_length)
        ]).arrange(RIGHT, buff=square_buffer)

        child_genes = VGroup(*[
            Square(side_length=0.7, fill_color=child_fill_color_initial,
                   fill_opacity=child_fill_opacity_initial, stroke_color=child_stroke_color_initial,
                   stroke_width=3)
            for _ in range(genome_length)
        ]).arrange(RIGHT, buff=square_buffer)

        genomes_group = VGroup(parent1_genes, parent2_genes, child_genes).arrange(DOWN, buff=0.7)
        self.add(genomes_group)

        p1_label = Text("Parent 1").next_to(parent1_genes, LEFT, buff=0.3)
        p2_label = Text("Parent 2").next_to(parent2_genes, LEFT, buff=0.3)
        child_label = Text("Child").next_to(child_genes, LEFT, buff=0.3)
        self.add(p1_label, p2_label, child_label)
        self.wait(0.5) # Shorter wait

        # 3. Indicate Crossover Points
        if genome_length == 0:
            return

        cp_line_y_start = parent1_genes.get_top()[1] + 0.1
        cp_line_y_end = child_genes.get_bottom()[1] - 0.1

        if 0 < cp1_idx <= genome_length:
            cp1_x = (parent1_genes[cp1_idx-1].get_right()[0] + parent1_genes[cp1_idx].get_left()[0]) / 2
            cp1_line = DashedLine(Point([cp1_x, cp_line_y_start, 0]), Point([cp1_x, cp_line_y_end, 0]), color=YELLOW)
            cp1_text = Text("CP1", font_size=24).move_to(Point([cp1_x, cp_line_y_start + 0.3, 0]))
            self.play(Create(cp1_line), Write(cp1_text))
        elif cp1_idx == 0:
            cp1_x = parent1_genes[0].get_left()[0] - square_buffer / 2 #  (parent1_genes[0].width / 2 + 0.05)
            cp1_line = DashedLine(Point([cp1_x, cp_line_y_start, 0]), Point([cp1_x, cp_line_y_end, 0]), color=YELLOW)
            cp1_text = Text("CP1", font_size=24).move_to(Point([cp1_x, cp_line_y_start + 0.3, 0]))
            self.play(Create(cp1_line), Write(cp1_text))

        if cp1_idx < cp2_idx < genome_length:
            cp2_x = (parent1_genes[cp2_idx-1].get_right()[0] + parent1_genes[cp2_idx].get_left()[0]) / 2
            cp2_line = DashedLine(Point([cp2_x, cp_line_y_start, 0]), Point([cp2_x, cp_line_y_end, 0]), color=YELLOW)
            cp2_text = Text("CP2", font_size=24).move_to(Point([cp2_x, cp_line_y_start + 0.3, 0]))
            self.play(Create(cp2_line), Write(cp2_text))
        elif cp2_idx == genome_length and cp1_idx < cp2_idx:
            cp2_x = parent1_genes[genome_length-1].get_right()[0] + square_buffer / 2 # (parent1_genes[genome_length-1].width / 2 + 0.05)
            cp2_line = DashedLine(Point([cp2_x, cp_line_y_start, 0]), Point([cp2_x, cp_line_y_end, 0]), color=YELLOW)
            cp2_text = Text("CP2", font_size=24).move_to(Point([cp2_x, cp_line_y_start + 0.3, 0]))
            self.play(Create(cp2_line), Write(cp2_text))

        self.wait(0.5) # Shorter wait

        # 4. Animate Gene Copying using TransformFromCopy
        # Segment 1: Parent 1 (indices 0 to cp1_idx - 1)
        if cp1_idx > 0:
            animations_seg1 = []
            for i in range(cp1_idx):
                # child_genes[i] (target) transforms from a copy of parent1_genes[i] (source)
                animations_seg1.append(TransformFromCopy(parent1_genes[i], child_genes[i]))
            self.play(AnimationGroup(*animations_seg1, lag_ratio=0.1))
            self.wait(0.5)

        # Segment 2: Parent 2 (indices cp1_idx to cp2_idx - 1)
        if cp2_idx > cp1_idx:
            animations_seg2 = []
            for i in range(cp1_idx, cp2_idx):
                animations_seg2.append(TransformFromCopy(parent2_genes[i], child_genes[i]))
            self.play(AnimationGroup(*animations_seg2, lag_ratio=0.1))
            self.wait(0.5)

        # Segment 3: Parent 1 (indices cp2_idx to genome_length - 1)
        if cp2_idx < genome_length:
            animations_seg3 = []
            for i in range(cp2_idx, genome_length):
                animations_seg3.append(TransformFromCopy(parent1_genes[i], child_genes[i]))
            self.play(AnimationGroup(*animations_seg3, lag_ratio=0.1))

        self.wait(1) # Final wait