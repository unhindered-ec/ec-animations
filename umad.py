import random
from manim import * # type: ignore
from enum import Enum, auto

# Indicates, during the addition phase, at which side of a gene (left or right)
# we're inserting a new gene.
class Side(Enum):
    LEFT = auto()
    RIGHT = auto()

class Umad(Scene):
    # --- CONFIGURATION ---
    # UMAD settings
    ADDITION_RATE: float = 0.3
    DELETION_RATE: float = 0.3

    # Genome settings
    GENOME_LENGTH: int = 10
    GENE_SIDE_LENGTH: float = 0.7
    GENE_STROKE_WIDTH: float = 2
    GENE_FILL_OPACITY: float = 0.8
    GENOME_BUFFER: float = 0.15

    # Parent/Child colors
    PARENT_GENE_COLOR: ManimColor = BLUE_E
    ADDED_GENE_COLOR: ManimColor = ORANGE
    DELETED_GENE_COLOR: ManimColor = RED

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
    TITLE: str = "UMAD mutation operator"
    TITLE_FONT_SIZE: int = 48
    SUBTITLE_FONT_SIZE: int = 30

    def setup(self):
        """
        Pre-builds all mobjects for the scene.

        The setup method is called by Manim before construct, so we can use it
        to create all the visual elements we'll need for the animation.
        """
        (
            self.parent_genes,
            self.addition_phase_genes,
            self.deletion_phase_genes,
            self.parent_label,
            self.addition_label,
            self.deletion_label,
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
            self.parent_genes, self.addition_phase_genes, self.deletion_phase_genes,
            self.parent_label, self.addition_label, self.deletion_label
        )

        all_mobjects = VGroup(self.title_text.next_to(individuals, UP, buff=1.3), individuals).center()

        self.arrow = Arrow(start=0.5*UP, end=0.5*DOWN, color=self.CROSSOVER_LINE_COLOR,
                           max_tip_length_to_length_ratio=0.5,
                           max_stroke_width_to_length_ratio=10)
        self.arrow.next_to(self.parent_genes[0], UP)

        self.add(all_mobjects)

        self.wait(0.5)

        # Animate the gene copying process.

        self.animate_additions()
        self.wait(1)
        self.animate_deletions()

        # parents = [self.parent1_genes, self.parent2_genes]
        # for index in range(self.GENOME_LENGTH):
        #     self.point_to_gene(self.parent1_genes[index])
        #     which_parent = random.choice(parents)
        #     # Highlight the parent gene chosen for copying
        #     self.play(Circumscribe(which_parent[index]), run_time=self.PARENT_GENE_HIGHLIGHT_RUN_TIME)
        #     # Copy the genes for a given gene from the appropriate parent to the child.
        #     self.copy_gene(index, which_parent, self.child_genes)

        # self.remove(self.arrow)

        # Final wait
        self.wait(1)

    def animate_additions(self):
        subtitle = "Addition phase"
        subtitle_text = Text(subtitle, font_size=self.SUBTITLE_FONT_SIZE, slant=ITALIC).next_to(self.title_text, DOWN, buff=0.25)
        self.add(subtitle_text)

        self.addition_phase_genes.become(self.parent_genes, match_center=True)
        self.play(TransformFromCopy(self.parent_genes, self.addition_phase_genes), run_time=self.GENE_COPY_RUN_TIME)

        for index in range(len(self.addition_phase_genes)):
            self.point_to_gene(self.addition_phase_genes[index])
            insert_here = random.random() < self.ADDITION_RATE
            if insert_here:
                which_side = random.choice(list(Side))


            # # Highlight the parent gene chosen for copying
            # self.play(Circumscribe(which_parent[index]), run_time=self.PARENT_GENE_HIGHLIGHT_RUN_TIME)
            # # Copy the genes for a given gene from the appropriate parent to the child.
            # self.copy_gene(index, which_parent, self.deletion_phase_genes)

            self.wait(0.1)

        self.remove(self.arrow)


        self.wait(0.25)

        self.remove(subtitle_text)
        pass

    def animate_deletions(self):
        subtitle = "Deletion phase"
        subtitle_text = Text(subtitle, font_size=self.SUBTITLE_FONT_SIZE, slant=ITALIC).next_to(self.title_text, DOWN, buff=0.5)
        self.add(subtitle_text)

        self.wait(0.25)

        self.remove(subtitle_text)
        pass

    def build_genomes(self) -> tuple[VGroup, VGroup, VGroup, Text, Text, Text]:
        """
        Builds the parent and child genome mobjects and their labels.

        This method creates the visual representations of the genomes and labels,
        arranges them, but does not add them to the scene.

        Returns:
            A tuple containing the mobjects for parent 1 genes, parent 2 genes,
            child genes, parent 1 label, parent 2 label, and child label.
        """
        parent_genes: VGroup = self.build_genome(self.PARENT_GENE_COLOR, self.PARENT_STROKE_COLOR)
        addition_phase_genes: VGroup = self.build_genome(self.CHILD_INITIAL_FILL_COLOR, self.CHILD_INITIAL_STROKE_COLOR)
        deletion_phase_genes: VGroup = self.build_genome(self.CHILD_INITIAL_FILL_COLOR, self.CHILD_INITIAL_STROKE_COLOR)

        # Arrange genomes vertically. This modifies the mobjects in place.
        VGroup(parent_genes, addition_phase_genes, deletion_phase_genes).arrange(DOWN, buff=self.GENOMES_VERTICAL_BUFFER)

        parent_label: Text = Text("Parent genes", font_size=self.LABEL_FONT_SIZE).next_to(parent_genes, LEFT, buff=self.LABEL_BUFFER)
        addition_label: Text = Text("Addition", font_size=self.LABEL_FONT_SIZE).next_to(addition_phase_genes, LEFT, buff=self.LABEL_BUFFER)
        deletion_label: Text = Text("Deletion", font_size=self.LABEL_FONT_SIZE).next_to(deletion_phase_genes, LEFT, buff=self.LABEL_BUFFER)

        return parent_genes, addition_phase_genes, deletion_phase_genes, parent_label, addition_label, deletion_label

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