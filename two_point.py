from manim import * # type: ignore

class TwoPointCrossoverScene(Scene):
    genome_length = 10
    gene_stroke_width = 2
    gene_fill_opacity = 0.8
    square_buffer = 0.15

    # The two crossover points will be to the _right_ of the genes
    # with the following indices. The code assume `0 ≤ cp1_idx < cp2_idx ≤ genome_length`
    cp1_idx = 2
    cp2_idx = 6
    assert 0 <= cp1_idx < cp2_idx <= genome_length

    def setup(self):
        self.parent1_genes, self.parent2_genes, self.child_genes = self.build_genomes()
        return super().setup()

    def construct(self):
        # Visualize the crossover points

        self.visualize_crossover_point(self.cp1_idx, "Crossover Point 1")
        self.visualize_crossover_point(self.cp2_idx, "Crossover Point 2")

        self.wait(0.5)

        # 4. Animate Gene Copying using TransformFromCopy
        # Segment 1: Parent 1 (indices 0 to cp1_idx - 1)
        if self.cp1_idx > 0:
            self.copy_genes(self.parent1_genes, self.child_genes, range(self.cp1_idx))
            self.wait(0.5)

        # Segment 2: Parent 2 (indices cp1_idx to cp2_idx - 1)
        if self.cp2_idx > self.cp1_idx:
            self.copy_genes(self.parent2_genes, self.child_genes, range(self.cp1_idx, self.cp2_idx))
            self.wait(0.5)

        # Segment 3: Parent 1 (indices cp2_idx to genome_length - 1)
        if self.cp2_idx < self.genome_length:
            self.copy_genes(self.parent1_genes, self.child_genes, range(self.cp2_idx, self.genome_length))

        # Final wait
        self.wait(1)

    def build_genomes(self):
        parent_1_color: ManimColor = BLUE_E
        parent_2_color: ManimColor = ORANGE
        parent_gene_stroke_color: ManimColor = BLACK

        child_fill_color_initial: ManimColor = BLACK
        child_stroke_color_initial: ManimColor = BLACK

        # 2. Create Parent and Child Genome Mobjects
        parent1_genes: VGroup = self.build_genome(parent_1_color, parent_gene_stroke_color)
        parent2_genes: VGroup = self.build_genome(parent_2_color, parent_gene_stroke_color)
        child_genes: VGroup = self.build_genome(child_fill_color_initial, child_stroke_color_initial)

        genomes_group: VGroup = VGroup(parent1_genes, parent2_genes, child_genes).arrange(DOWN, buff=0.7)
        # self.add(genomes_group)

        p1_label: Text = Text("Parent 1").next_to(parent1_genes, LEFT, buff=2*self.square_buffer)
        p2_label: Text = Text("Parent 2").next_to(parent2_genes, LEFT, buff=2*self.square_buffer)
        child_label: Text = Text("Child").next_to(child_genes, LEFT, buff=2*self.square_buffer)

        self.add(VGroup(genomes_group, p1_label, p2_label, child_label).center())

        # self.add(p1_label, p2_label, child_label)
        # Shorter wait
        self.wait(0.5)
        return parent1_genes,parent2_genes,child_genes

    def build_genome(self, fill_color: ManimColor, stroke_color: ManimColor):
        return VGroup(*[
            Square(side_length=0.7, fill_color=fill_color, fill_opacity=self.gene_fill_opacity,
                   stroke_color=stroke_color, stroke_width=self.gene_stroke_width)
            for _ in range(self.genome_length)
        ]).arrange(RIGHT, buff=self.square_buffer)

    def visualize_crossover_point(self, gap_index, label):
        # These specify the top and bottom y-coordinates of the dashed lines representing
        # the crossover points. We want the lines to start slightly above the first parent
        # (hence the +0.1) and end slightly below the child (hence the -0.1).
        cp_line_y_start = self.parent1_genes.get_top()[1] + 0.1
        cp_line_y_end = self.child_genes.get_bottom()[1] - 0.1

        if gap_index < self.genome_length:
            # Set the x-coordinate of the crossover line to be a little to the left of the gene at `gap_index`.
            x_coordinate = self.parent1_genes[gap_index].get_left()[0] - self.square_buffer / 2
        else:
            # Here the crossover line is to the right of all the genes, so we set its x-coordinate to be a little
            # to the right of the last gene.
            x_coordinate = self.parent1_genes[-1].get_right()[0] + self.square_buffer / 2
        line = DashedLine(
            Point(np.array([x_coordinate, cp_line_y_start, 0])),
            Point(np.array([x_coordinate, cp_line_y_end, 0])),
            color=YELLOW,
            dash_length=0.15,
            dashed_ratio=0.70
        )
        text = Text(label, font_size=24).move_to(Point(np.array([x_coordinate, cp_line_y_start + 0.3, 0])))
        self.add(text)
        self.play(Create(line))

    def copy_genes(self, from_genes, to_genes, gene_range):
        animations = []
        for i in gene_range:
            # Set the target genome square to have the same color, etc., as the parent genome.
            # We have to set `match_center` to `True` or it will also set the child's position
            # to match parent, and nothing happens in the animation.
            to_genes[i].become(from_genes[i], match_center=True)
            animations.append(TransformFromCopy(from_genes[i], to_genes[i]))
        self.play(AnimationGroup(*animations, lag_ratio=0.1))
