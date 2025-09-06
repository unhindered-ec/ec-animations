import random
from manim import * # type: ignore

class UniformCrossoverScene(Scene):
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
    GENOMES_VERTICAL_BUFFER: float = 0.5
    LABEL_BUFFER: float = 0.3
    LABEL_FONT_SIZE: int = 36

    # Crossover settings
    CROSSOVER_LINE_COLOR: ManimColor = YELLOW

    # Animation settings
    ARROW_RUN_TIME: float = 0.25
    PARENT_GENE_HIGHLIGHT_RUN_TIME: float = 0.75
    GENE_COPY_RUN_TIME: float = 0.5

    # Titles and labels
    TITLE: str = "Uniform Crossover"
    TITLE_FONT_SIZE: int = 48

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

        self.title_text = Text(self.TITLE, font_size=self.TITLE_FONT_SIZE)

        # This seed gave us a nice distribution, at least when we ran it on 30 Aug 2025
        # 1001110110
        random.seed(5)

        super().setup()

    def construct(self):
        """Defines the animation sequence for uniform crossover."""
        # Group all genomes and labels, center them, and add them to the scene.
        individuals = VGroup(
            self.parent1_genes, self.parent2_genes, self.child_genes,
            self.p1_label, self.p2_label, self.child_label
        )

        all_mobjects = VGroup(self.title_text.next_to(individuals, UP, buff=1.3), individuals).center()

        self.arrow = Arrow(start=0.5*UP, end=0.5*DOWN, color=self.CROSSOVER_LINE_COLOR,
                           max_tip_length_to_length_ratio=0.5,
                           max_stroke_width_to_length_ratio=10)
        self.arrow.next_to(self.parent1_genes[0], UP)

        self.add(all_mobjects)

        self.wait(0.5)

        # Animate the gene copying process.

        parents = [self.parent1_genes, self.parent2_genes]
        for index in range(self.GENOME_LENGTH):
            self.point_to_gene(self.parent1_genes[index])
            which_parent = random.choice(parents)
            # Highlight the parent gene chosen for copying
            self.play(Circumscribe(which_parent[index]), run_time=self.PARENT_GENE_HIGHLIGHT_RUN_TIME)
            # Copy the genes for a given gene from the appropriate parent to the child.
            self.copy_gene(index, which_parent, self.child_genes)

        self.remove(self.arrow)

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


    def point_to_gene(self, gene: Mobject):
        self.play(self.arrow.animate.next_to(gene, UP), run_time=self.ARROW_RUN_TIME)

    def copy_gene(self, index: int, from_genes: VGroup, to_genes: VGroup):
        """
        Animates the copying of a single gene from a parent to the child.

        Args:
            index: The position of the gene being copied.
            from_genes: The parent genome mobject to copy from.
            to_genes: The child genome mobject to copy to.
        """
        # Set the target genome square to have the same color, etc., as the parent genome.
        # We must set `match_center` to `True`, otherwise the child's position will also
        # be set to match the parent's, and the gene will not appear to move.
        to_genes[index].become(from_genes[index], match_center=True)
        self.play(TransformFromCopy(from_genes[index], to_genes[index]), run_time=self.GENE_COPY_RUN_TIME)