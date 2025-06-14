from manim import *

class TwoPointCrossoverScene(Scene):
    genome_length = 10
    gene_stroke_width = 2
    gene_fill_opacity = 0.8
    square_buffer = 0.05

    def construct(self):
        # 1. Define parameters
        cp1_idx = 2
        cp2_idx = 6

        parent1_genes, parent2_genes, child_genes = self.build_genomes()

        # 3. Indicate Crossover Points
        if self.genome_length == 0:
            return

        cp_line_y_start = parent1_genes.get_top()[1] + 0.1
        cp_line_y_end = child_genes.get_bottom()[1] - 0.1

        if 0 < cp1_idx <= self.genome_length:
            cp1_x = (parent1_genes[cp1_idx-1].get_right()[0] + parent1_genes[cp1_idx].get_left()[0]) / 2
            cp1_line = DashedLine(Point(np.array([cp1_x, cp_line_y_start, 0])), Point(np.array([cp1_x, cp_line_y_end, 0])), color=YELLOW, dash_length=0.15, dashed_ratio=0.70)
            cp1_text = Text("Crossover Point 1", font_size=24).move_to(Point(np.array([cp1_x, cp_line_y_start + 0.3, 0])))
            self.add(cp1_text)
            self.play(Create(cp1_line))
        elif cp1_idx == 0:
            cp1_x = parent1_genes[0].get_left()[0] - self.square_buffer / 2
            cp1_line = DashedLine(Point(np.array([cp1_x, cp_line_y_start, 0])), Point(np.array([cp1_x, cp_line_y_end, 0])), color=YELLOW, dash_length=0.15, dashed_ratio=0.70)
            cp1_text = Text("Crossover Point 1", font_size=24).move_to(Point(np.array([cp1_x, cp_line_y_start + 0.3, 0])))
            self.add(cp1_text)
            self.play(Create(cp1_line))

        if cp1_idx < cp2_idx < self.genome_length:
            cp2_x = (parent1_genes[cp2_idx-1].get_right()[0] + parent1_genes[cp2_idx].get_left()[0]) / 2
            cp2_line = DashedLine(Point(np.array([cp2_x, cp_line_y_start, 0])), Point(np.array([cp2_x, cp_line_y_end, 0])), color=YELLOW, dash_length=0.15, dashed_ratio=0.70)
            cp2_text = Text("Crossover Point 2", font_size=24).move_to(Point(np.array([cp2_x, cp_line_y_start + 0.3, 0])))
            self.add(cp2_text)
            self.play(Create(cp2_line))
        elif cp2_idx == self.genome_length and cp1_idx < cp2_idx:
            cp2_x = parent1_genes[self.genome_length-1].get_right()[0] + self.square_buffer / 2
            cp2_line = DashedLine(Point(np.array([cp2_x, cp_line_y_start, 0])), Point(np.array([cp2_x, cp_line_y_end, 0])), color=YELLOW, dash_length=0.15, dashed_ratio=0.70)
            cp2_text = Text("Crossover Point 2", font_size=24).move_to(Point(np.array([cp2_x, cp_line_y_start + 0.3, 0])))
            self.add(cp2_text)
            self.play(Create(cp2_line))

        self.wait(0.5) # Shorter wait

        # 4. Animate Gene Copying using TransformFromCopy
        # Segment 1: Parent 1 (indices 0 to cp1_idx - 1)
        if cp1_idx > 0:
            animations_seg1 = []
            for i in range(cp1_idx):
                # Set the child genome square to have the same color, etc., as the parent genome.
                # We have to set `match_center` to `True` or it will also set the child's position
                # to match parent, and nothing in the animation.
                child_genes[i].become(parent1_genes[i], match_center=True)
                # child_genes[i] (target) transforms from a copy of parent1_genes[i] (source)
                animations_seg1.append(TransformFromCopy(parent1_genes[i], child_genes[i]))
            self.play(AnimationGroup(*animations_seg1, lag_ratio=0.1))
            self.wait(0.5)

        # Segment 2: Parent 2 (indices cp1_idx to cp2_idx - 1)
        if cp2_idx > cp1_idx:
            animations_seg2 = []
            for i in range(cp1_idx, cp2_idx):
                child_genes[i].become(parent2_genes[i], match_center=True)
                animations_seg2.append(TransformFromCopy(parent2_genes[i], child_genes[i]))
            self.play(AnimationGroup(*animations_seg2, lag_ratio=0.1))
            self.wait(0.5)

        # Segment 3: Parent 1 (indices cp2_idx to genome_length - 1)
        if cp2_idx < self.genome_length:
            animations_seg3 = []
            for i in range(cp2_idx, self.genome_length):
                child_genes[i].become(parent1_genes[i], match_center=True)
                animations_seg3.append(TransformFromCopy(parent1_genes[i], child_genes[i]))
            self.play(AnimationGroup(*animations_seg3, lag_ratio=0.1))

        # Final wait
        self.wait(1)

    def build_genomes(self):
        parent_1_color: ManimColor = BLUE_C
        parent_2_color: ManimColor = GREEN_C
        parent_gene_stroke_color: ManimColor = BLACK

        child_fill_color_initial: ManimColor = BLACK
        child_stroke_color_initial: ManimColor = WHITE

        # 2. Create Parent and Child Genome Mobjects
        parent1_genes: VGroup = self.build_genome(parent_1_color, parent_gene_stroke_color)
        parent2_genes: VGroup = self.build_genome(parent_2_color, parent_gene_stroke_color)
        child_genes: VGroup = self.build_genome(child_fill_color_initial, child_stroke_color_initial)

        genomes_group: VGroup = VGroup(parent1_genes, parent2_genes, child_genes).arrange(DOWN, buff=0.7)
        self.add(genomes_group)

        p1_label: Text = Text("Parent 1").next_to(parent1_genes, LEFT, buff=0.3)
        p2_label: Text = Text("Parent 2").next_to(parent2_genes, LEFT, buff=0.3)
        child_label: Text = Text("Child").next_to(child_genes, LEFT, buff=0.3)
        self.add(p1_label, p2_label, child_label)
        # Shorter wait
        self.wait(0.5)
        return parent1_genes,parent2_genes,child_genes

    def build_genome(self, fill_color: ManimColor, stroke_color: ManimColor):
        return VGroup(*[
            Square(side_length=0.7, fill_color=fill_color, fill_opacity=self.gene_fill_opacity,
                   stroke_color=stroke_color, stroke_width=self.gene_stroke_width)
            for _ in range(self.genome_length)
        ]).arrange(RIGHT, buff=self.square_buffer)