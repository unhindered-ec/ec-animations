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
        """
        Pre-builds all mobjects for the scene.

        The setup method is called by Manim before construct, so we can use it
        to create all the visual elements we'll need for the animation.
        """
        (
            self.parent1_genes,
            self.parent2_genes,
            self.child_genes,
            self.p1_label,
            self.p2_label,
            self.child_label,
        ) = self.build_genomes()
        super().setup()

    def construct(self):
        """Defines the animation sequence for the two-point crossover."""
        # Group all genomes and labels, center them, and add them to the scene.
        all_mobjects = VGroup(
            self.parent1_genes, self.parent2_genes, self.child_genes,
            self.p1_label, self.p2_label, self.child_label
        ).center()
        self.add(all_mobjects)
        self.wait(0.5)

        # Visualize the crossover points
        cp1_line, cp1_text = self.visualize_crossover_point(self.CROSSOVER_POINT_1_INDEX, "Crossover Point 1")
        cp2_line, cp2_text = self.visualize_crossover_point(self.CROSSOVER_POINT_2_INDEX, "Crossover Point 2")

        self.add(cp1_text, cp2_text)
        self.play(Create(cp1_line), Create(cp2_line))
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

    def build_genomes(self) -> tuple[VGroup, VGroup, VGroup, Text, Text, Text]:
        """
        Builds the parent and child genome mobjects and their labels.

        This method creates the visual representations of the genomes and labels,
        arranges them, but does not add them to the scene.

        Returns:
            A tuple containing the mobjects for parent 1 genes, parent 2 genes,
            child genes, parent 1 label, parent 2 label, and child label.
        """
        parent1_genes: VGroup = self.build_genome(self.FIRST_PARENT_COLOR, self.PARENT_STROKE_COLOR)
        parent2_genes: VGroup = self.build_genome(self.SECOND_PARENT_COLOR, self.PARENT_STROKE_COLOR)
        child_genes: VGroup   = self.build_genome(self.CHILD_INITIAL_FILL_COLOR, self.CHILD_INITIAL_STROKE_COLOR)

        # Arrange genomes vertically. This modifies the mobjects in place.
        VGroup(parent1_genes, parent2_genes, child_genes).arrange(DOWN, buff=self.GENOMES_VERTICAL_BUFFER)

        p1_label: Text    = Text("Parent 1", font_size=self.LABEL_FONT_SIZE).next_to(parent1_genes, LEFT, buff=self.LABEL_BUFFER)
        p2_label: Text    = Text("Parent 2", font_size=self.LABEL_FONT_SIZE).next_to(parent2_genes, LEFT, buff=self.LABEL_BUFFER)
        child_label: Text = Text("Child", font_size=self.LABEL_FONT_SIZE).next_to(child_genes, LEFT, buff=self.LABEL_BUFFER)

        return parent1_genes, parent2_genes, child_genes, p1_label, p2_label, child_label

    def build_genome(self, fill_color: ManimColor, stroke_color: ManimColor) -> VGroup:
        """Builds a single genome as a VGroup of squares."""
        return VGroup(*[
            Square(side_length=self.GENE_SIDE_LENGTH, fill_color=fill_color, fill_opacity=self.GENE_FILL_OPACITY,
                   stroke_color=stroke_color, stroke_width=self.GENE_STROKE_WIDTH)
            for _ in range(self.GENOME_LENGTH)
        ]).arrange(RIGHT, buff=self.GENOME_BUFFER)

    def visualize_crossover_point(self, gap_index: int, label: str) -> tuple[DashedLine, Text]:
        """
        Creates the dashed line and label for a crossover point.

        Args:
            gap_index: The index of the gene to the right of the crossover point.
            label: The text to display for the crossover point label.

        Returns:
            A tuple containing the DashedLine and Text mobjects.
        """
        # Specify the y-coordinates for the top and bottom of the crossover line.
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
        return line, text

    def copy_genes(self, from_genes: VGroup, to_genes: VGroup, gene_range: range):
        """
        Animates the copying of genes from a parent to the child.

        Args:
            from_genes: The parent genome mobject to copy from.
            to_genes: The child genome mobject to copy to.
            gene_range: The range of gene indices to copy.
        """
        animations = []
        for i in gene_range:
            # Set the target genome square to have the same color, etc., as the parent genome.
            # We must set `match_center` to `True`, otherwise the child's position will also
            # be set to match the parent's, and the gene will not appear to move.
            to_genes[i].become(from_genes[i], match_center=True)
            animations.append(TransformFromCopy(from_genes[i], to_genes[i]))
        self.play(AnimationGroup(*animations, lag_ratio=self.ANIMATION_COPY_LAG_RATIO))
