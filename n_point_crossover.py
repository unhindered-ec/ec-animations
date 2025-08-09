from typing import cast
from manim import * # type: ignore

class NPointCrossoverScene(Scene):
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
    CROSSOVER_POINTS: list[int] = [2, 6, 7]
    CROSSOVER_LINE_COLOR: ManimColor = YELLOW
    CROSSOVER_LINE_DASH_LENGTH: float = 0.15
    CROSSOVER_LINE_DASH_RATIO: float = 0.70
    CROSSOVER_LABEL_FONT_SIZE: int = 36
    CROSSOVER_LINE_Y_PADDING: float = 0.1
    CROSSOVER_LABEL_Y_OFFSET: float = 0.3
    CROSSOVER_RAY_COLOR: ManimColor = YELLOW

    # Animation settings
    CROSSOVER_POINT_LAG_RATIO = 0.5
    GENE_COPY_LAG_RATIO: float = 0.1

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

        # The crossover points must be sorted and unique, and within the valid range of the genome.
        # Crossover points are located *before* the genes at the specified indices.
        assert len(self.CROSSOVER_POINTS) == len(set(self.CROSSOVER_POINTS)), "CROSSOVER_POINTS must contain unique values."
        assert self.CROSSOVER_POINTS == sorted(self.CROSSOVER_POINTS), "CROSSOVER_POINTS must be sorted."
        assert all(0 <= cp <= self.GENOME_LENGTH for cp in self.CROSSOVER_POINTS), \
            "All crossover points must be within the range [0, GENOME_LENGTH]."

        super().setup()

    def construct(self):
        """Defines the animation sequence for N-point crossover."""
        # Group all genomes and labels, center them, and add them to the scene.
        all_mobjects = VGroup(
            self.parent1_genes, self.parent2_genes, self.child_genes,
            self.p1_label, self.p2_label, self.child_label
        ).center()
        self.add(all_mobjects)

        crossover_lines, crossover_text, crossover_rays = self.build_crossover_visualization()

        self.add(VGroup(crossover_text)) # Add texts instantly

        self.wait(0.5)

        if len(crossover_lines) == 1:
            self.play(Create(cast(VMobject, crossover_lines[0])))
        else:
            self.play(
                AnimationGroup(
                    [
                        AnimationGroup(
                            ShowPassingFlash(ray, run_time=1, time_width=0.5),
                            Create(line),
                            lag_ratio=0
                        )
                        for (line, ray) in zip(crossover_lines, crossover_rays)
                    ],
                    lag_ratio=self.CROSSOVER_POINT_LAG_RATIO
                )
            )

        self.wait(0.5)

        # Animate the gene copying process.

        previous_crossover = 0
        parents = [self.parent1_genes, self.parent2_genes]
        # Add `self.GENOME_LENGTH` as a implied crossover point at the end.
        for index, crossover_point in enumerate(self.CROSSOVER_POINTS + [self.GENOME_LENGTH]):
            # Copy the genes for a given segment from the appropriate parent to the child.
            self.copy_genes(parents[index % 2], self.child_genes, range(previous_crossover, crossover_point))
            previous_crossover = crossover_point

        # Final wait
        self.wait(1)

    def build_crossover_visualization(self) -> tuple[VGroup, Text, VGroup]:
        """
        Builds the crossover point visualization objects.

        This method creates the visual representations of

        - The crossover points (as a `VGroup` of dashed lines)
        - The label for the crossover points (as a `Text` MObject)
        - The rays connecting the label to the crossover points (as a `VGroup` of lines)

        Returns:
            A tuple containing the mobjects for the crossover point dashed lines,
            the label, and the mobjects for the rays.
        """
        crossover_lines = VGroup()
        crossover_rays = VGroup()

        for index, crossover_point in enumerate(self.CROSSOVER_POINTS):
            dashed_line = self.visualize_crossover_point(crossover_point)
            crossover_lines.add(dashed_line)

        num_crossover_points = len(self.CROSSOVER_POINTS)
        if num_crossover_points == 1:
            label = "Crossover point"
            text = Text(label, font_size=self.CROSSOVER_LABEL_FONT_SIZE).next_to(crossover_lines[0], UP)
            crossover_text = text
        else:
            label = "Crossover points"
            text = Text(label, font_size=self.CROSSOVER_LABEL_FONT_SIZE).next_to(self.parent1_genes, UP, buff=1)
            crossover_text = text
            for line in crossover_lines:
                start = text.get_bottom()
                end = line.get_top()
                ray = Line(start, end, color = self.CROSSOVER_RAY_COLOR)
                crossover_rays.add(ray)

        return crossover_lines, crossover_text, crossover_rays

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
        child_genes: VGroup = self.build_genome(self.CHILD_INITIAL_FILL_COLOR, self.CHILD_INITIAL_STROKE_COLOR)

        # Arrange genomes vertically. This modifies the mobjects in place.
        VGroup(parent1_genes, parent2_genes, child_genes).arrange(DOWN, buff=self.GENOMES_VERTICAL_BUFFER)

        p1_label: Text = Text("Parent 1", font_size=self.LABEL_FONT_SIZE).next_to(parent1_genes, LEFT, buff=self.LABEL_BUFFER)
        p2_label: Text = Text("Parent 2", font_size=self.LABEL_FONT_SIZE).next_to(parent2_genes, LEFT, buff=self.LABEL_BUFFER)
        child_label: Text = Text("Child", font_size=self.LABEL_FONT_SIZE).next_to(child_genes, LEFT, buff=self.LABEL_BUFFER)

        return parent1_genes, parent2_genes, child_genes, p1_label, p2_label, child_label

    def build_genome(self, fill_color: ManimColor, stroke_color: ManimColor) -> VGroup:
        """Builds a single genome as a VGroup of squares."""
        return VGroup(*[
            Square(side_length=self.GENE_SIDE_LENGTH, fill_color=fill_color, fill_opacity=self.GENE_FILL_OPACITY,
                   stroke_color=stroke_color, stroke_width=self.GENE_STROKE_WIDTH)
            for _ in range(self.GENOME_LENGTH)
        ]).arrange(RIGHT, buff=self.GENOME_BUFFER)

    def visualize_crossover_point(self, gap_index: int) -> DashedLine:
        """
        Creates the dashed line for a crossover point.

        Args:
            gap_index: The index of the first gene immediately after the crossover point.
            label: The text to display for the crossover point label.

        Returns:
            The DashedLine Text mobject.
        """
        # Specify the y-coordinates for the top and bottom of the crossover line
        cp_line_y_start = self.parent1_genes.get_top()[1] + self.CROSSOVER_LINE_Y_PADDING
        cp_line_y_end = self.child_genes.get_bottom()[1] - self.CROSSOVER_LINE_Y_PADDING

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
        return line

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
        self.play(AnimationGroup(*animations, lag_ratio=self.GENE_COPY_LAG_RATIO))
