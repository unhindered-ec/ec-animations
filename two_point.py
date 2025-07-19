from manim import * # type: ignore

class TwoPointCrossoverScene(Scene):
    # --- CONFIGURATION ---
    # Genome settings
    GENOME_LENGTH: int = 10
    GENE_SIDE_LENGTH: float = 0.7
    GENE_STROKE_WIDTH: float = 2
    GENE_FILL_OPACITY: float = 0.8
    GENOME_BUFFER: float = 0.15

    # Parent/Child colors
    FIRST_PARENT_COLOR: ManimColor = BLUE_E
    SECOND_PARENT_COLOR: ManimColor = ORANGE
    PARENT_STROKE_COLOR: ManimColor = BLACK
    CHILD_INITIAL_FILL_COLOR: ManimColor = BLACK
    CHILD_INITIAL_STROKE_COLOR: ManimColor = BLACK

    # Layout settings
    GENOMES_VERTICAL_BUFFER: float = 0.7
    LABEL_BUFFER: float = 0.3
    LABEL_FONT_SIZE: int = 36

    # Crossover settings
    CROSSOVER_POINT_1_INDEX: int = 2
    CROSSOVER_POINT_2_INDEX: int = 6
    CROSSOVER_LINE_COLOR: ManimColor = YELLOW
    CROSSOVER_LINE_DASH_LENGTH: float = 0.15
    CROSSOVER_LINE_DASH_RATIO: float = 0.70
    CROSSOVER_LABEL_FONT_SIZE: int = 24
    CROSSOVER_LINE_Y_PADDING: float = 0.1
    CROSSOVER_LABEL_Y_OFFSET: float = 0.3

    # Animation settings
    ANIMATION_COPY_LAG_RATIO: float = 0.1

    # The two crossover points will be to the _right_ of the genes
    # with the following indices. The code assumes `0 ≤ CROSSOVER_POINT_1_INDEX < CROSSOVER_POINT_2_INDEX ≤ GENOME_LENGTH`.
    assert 0 <= CROSSOVER_POINT_1_INDEX < CROSSOVER_POINT_2_INDEX <= GENOME_LENGTH, "Crossover points are not valid."

    def setup(self):
        self.parent1_genes, self.parent2_genes, self.child_genes = self.build_genomes()
        return super().setup()

    def construct(self):
        # Visualize the crossover points

        self.visualize_crossover_point(self.CROSSOVER_POINT_1_INDEX, "Crossover Point 1")
        self.visualize_crossover_point(self.CROSSOVER_POINT_2_INDEX, "Crossover Point 2")

        self.wait(0.5)

        # Animate the gene copying process using TransformFromCopy.
        # Segment 1: From Parent 1 (indices 0 to CROSSOVER_POINT_1_INDEX - 1)
        if self.CROSSOVER_POINT_1_INDEX > 0:
            self.copy_genes(self.parent1_genes, self.child_genes, range(self.CROSSOVER_POINT_1_INDEX))
            self.wait(0.5)

        # Segment 2: From Parent 2 (indices CROSSOVER_POINT_1_INDEX to CROSSOVER_POINT_2_INDEX - 1)
        if self.CROSSOVER_POINT_2_INDEX > self.CROSSOVER_POINT_1_INDEX:
            self.copy_genes(self.parent2_genes, self.child_genes, range(self.CROSSOVER_POINT_1_INDEX, self.CROSSOVER_POINT_2_INDEX))
            self.wait(0.5)

        # Segment 3: From Parent 1 (indices CROSSOVER_POINT_2_INDEX to GENOME_LENGTH - 1)
        if self.CROSSOVER_POINT_2_INDEX < self.GENOME_LENGTH:
            self.copy_genes(self.parent1_genes, self.child_genes, range(self.CROSSOVER_POINT_2_INDEX, self.GENOME_LENGTH))

        # Final wait
        self.wait(1)

    def build_genomes(self):
        # Create Parent and Child Genome Mobjects
        parent1_genes: VGroup = self.build_genome(self.FIRST_PARENT_COLOR, self.PARENT_STROKE_COLOR)
        parent2_genes: VGroup = self.build_genome(self.SECOND_PARENT_COLOR, self.PARENT_STROKE_COLOR)
        child_genes: VGroup = self.build_genome(self.CHILD_INITIAL_FILL_COLOR, self.CHILD_INITIAL_STROKE_COLOR)

        genomes_group: VGroup = VGroup(parent1_genes, parent2_genes, child_genes).arrange(DOWN, buff=self.GENOMES_VERTICAL_BUFFER)

        p1_label: Text = Text("Parent 1", font_size=self.LABEL_FONT_SIZE).next_to(parent1_genes, LEFT, buff=self.LABEL_BUFFER)
        p2_label: Text = Text("Parent 2", font_size=self.LABEL_FONT_SIZE).next_to(parent2_genes, LEFT, buff=self.LABEL_BUFFER)
        child_label: Text = Text("Child", font_size=self.LABEL_FONT_SIZE).next_to(child_genes, LEFT, buff=self.LABEL_BUFFER)

        self.add(VGroup(genomes_group, p1_label, p2_label, child_label).center())

        self.wait(0.5)
        return parent1_genes,parent2_genes,child_genes

    def build_genome(self, fill_color: ManimColor, stroke_color: ManimColor):
        return VGroup(*[
            Square(side_length=self.GENE_SIDE_LENGTH, fill_color=fill_color, fill_opacity=self.GENE_FILL_OPACITY,
                   stroke_color=stroke_color, stroke_width=self.GENE_STROKE_WIDTH)
            for _ in range(self.GENOME_LENGTH)
        ]).arrange(RIGHT, buff=self.GENOME_BUFFER)

    def visualize_crossover_point(self, gap_index, label):
        # These specify the top and bottom y-coordinates of the dashed lines representing
        # the crossover points. We want the lines to start slightly above the first parent
        # (hence the padding) and end slightly below the child (hence the padding).
        cp_line_y_start = self.parent1_genes.get_top()[1] + self.CROSSOVER_LINE_Y_PADDING
        cp_line_y_end   = self.child_genes.get_bottom()[1] - self.CROSSOVER_LINE_Y_PADDING

        if gap_index < self.GENOME_LENGTH:
            # Set the x-coordinate of the crossover line to be a little to the left of the gene at `gap_index`.
            x_coordinate = self.parent1_genes[gap_index].get_left()[0] - (self.GENOME_BUFFER / 2)
        else:
            # Here the crossover line is to the right of all the genes, so we set its x-coordinate to be a little
            # to the right of the last gene.
            x_coordinate = self.parent1_genes[-1].get_right()[0] + (self.GENOME_BUFFER / 2)
        line = DashedLine(
            Point(np.array([x_coordinate, cp_line_y_start, 0])),
            Point(np.array([x_coordinate, cp_line_y_end, 0])),
            color=self.CROSSOVER_LINE_COLOR,
            dash_length=self.CROSSOVER_LINE_DASH_LENGTH,
            dashed_ratio=self.CROSSOVER_LINE_DASH_RATIO
        )
        text = Text(label, font_size=self.CROSSOVER_LABEL_FONT_SIZE).move_to(
            Point(np.array([x_coordinate, cp_line_y_start + self.CROSSOVER_LABEL_Y_OFFSET, 0]))
        )
        self.add(text)
        self.play(Create(line))

    def copy_genes(self, from_genes, to_genes, gene_range):
        animations = []
        for i in gene_range:
            # Set the target genome square to have the same color, etc., as the parent genome.
            # We must set `match_center` to `True`, otherwise the child's position will also
            # be set to match the parent's, and the gene will not appear to move.
            to_genes[i].become(from_genes[i], match_center=True)
            animations.append(TransformFromCopy(from_genes[i], to_genes[i]))
        self.play(AnimationGroup(*animations, lag_ratio=self.ANIMATION_COPY_LAG_RATIO))
