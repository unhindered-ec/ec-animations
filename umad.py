import random
from manim import *
from enum import Enum, auto
from typing import Optional, cast
from copy import deepcopy

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
    GENOME_LENGTH: int = 5
    GENE_SIDE_LENGTH: float = 0.8
    GENE_STROKE_WIDTH: float = 2
    GENE_FILL_OPACITY: float = 0.8
    GENOME_BUFFER: float = 0.15
    GENE_FONT_SIZE: int = 30

    # Parent/Child colors
    PARENT_GENE_COLOR: ManimColor = BLUE_E
    ADDED_GENE_COLOR: ManimColor = GREEN
    DELETED_GENE_COLOR: ManimColor = RED

    PARENT_STROKE_COLOR: ManimColor = BLACK
    CHILD_INITIAL_FILL_COLOR: ManimColor = BLACK
    CHILD_INITIAL_STROKE_COLOR: ManimColor = BLACK
    CHILD_ARROW_LENGTH: float = GENE_SIDE_LENGTH / 2

    # Layout settings
    GENOMES_VERTICAL_BUFFER: float = 1
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
    TITLE_OFFSET = 0.7

    def setup(self):
        """
        Pre-builds all mobjects for the scene.

        The setup method is called by Manim before construct, so we can use it
        to create all the visual elements we'll need for the animation.
        """
        (
            self.parent_genes,
            self.parent_label,
            self.addition_label,
            self.deletion_label,
        ) = self.build_labels_and_initial_genome()

        self.title_text = Text(self.TITLE, font_size=self.TITLE_FONT_SIZE)

        random.seed(5)

        super().setup()

    def construct(self):
        """Defines the animation sequence for uniform crossover."""
        # Group all the labels and the initial genome, and add them to the scene, aligned to the left.
        labels_and_genes = VGroup(
            self.parent_genes,
            self.parent_label, self.addition_label, self.deletion_label
        ).to_edge(LEFT)

        title = self.title_text.next_to(labels_and_genes, UP, buff=self.TITLE_OFFSET)
        center = title.get_center()
        center[1] = 0
        title = title.shift(-center)

        all_mobjects = VGroup(title, labels_and_genes)
        center = all_mobjects.get_center()
        center[0] = 0
        all_mobjects = all_mobjects.shift(-center)

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
        self.addition_label.set_opacity(1)

        # Make a copy of the parent genes for the addition phase
        self.addition_phase_genes = self.parent_genes.copy().next_to(self.addition_label, RIGHT)
        self.play(TransformFromCopy(self.parent_genes, self.addition_phase_genes), run_time=self.GENE_COPY_RUN_TIME)

        # The distance between two adjacent genes
        shift_distance = self.addition_phase_genes[1].get_center() - self.addition_phase_genes[0].get_center()

        # A VGroup that will contain all the parent genes and all the newly inserted child genes.
        final_addition_phase_genes: VGroup = VGroup()

        current_parent_gene_position = 0
        for index in range(len(self.addition_phase_genes)):
            gene = self.addition_phase_genes[current_parent_gene_position]
            self.point_to_gene(gene)
            self.play(Circumscribe(gene), run_time=self.PARENT_GENE_HIGHLIGHT_RUN_TIME)
            insert_here = random.random() < self.ADDITION_RATE
            if insert_here:
                which_side = random.choice(list(Side))
                # `shift_start` is the index of the first gene that will need to be shifted to
                # the right to make room for the new gene.
                shift_start = current_parent_gene_position
                if which_side == Side.RIGHT:
                    shift_start += 1
                changes = [MoveAlongPath(gene, Line(gene.get_center(), gene.get_center() + shift_distance))
                           for gene in self.addition_phase_genes[shift_start:]]
                # If the inserted gene is on the left, then we also need to shift the
                # arrow the width of one gene to the right.
                if which_side == Side.LEFT:
                    changes.append(
                        MoveAlongPath(self.arrow, Line(self.arrow.get_center(), self.arrow.get_center() + shift_distance))
                    )
                child_gene = self.build_gene(self.ADDED_GENE_COLOR, self.PARENT_STROKE_COLOR, current_parent_gene_position, which_side)
                # Placing the gene is awkward because of the arrow, which changes the width of the
                # gene's VGroup.
                #
                # The `move_to` calls position according to `child_gene.get_center()`, but we want
                # to position according to `child_gene[0].get_center()` (the center of the child gene's
                # box), so we shift by the difference between those two centers.
                if which_side == Side.LEFT:
                    child_gene.move_to(gene.get_center())
                    final_addition_phase_genes.add(*[child_gene, gene])
                else:
                    child_gene.move_to(
                        gene.get_center() + RIGHT * (self.GENE_SIDE_LENGTH + self.GENOME_BUFFER)
                    )
                    final_addition_phase_genes.add(*[gene, child_gene])
                child_gene.shift(child_gene.get_center() - child_gene[0].get_center())

                self.add(child_gene)
                self.play(
                    AnimationGroup(changes),
                    rate_func=rate_functions.ease_in_out_sine)
            else:
                final_addition_phase_genes.add(cast(VMobject, gene))

            current_parent_gene_position += 1

            self.wait(0.1)

        self.addition_phase_genes: VGroup = VGroup()
        for index, gene in enumerate(final_addition_phase_genes):
            gene_copy = self.build_gene(self.PARENT_GENE_COLOR, self.PARENT_STROKE_COLOR, index, label = cast(VMobject, deepcopy(gene[1])))
            self.addition_phase_genes.add(gene_copy)
        self.addition_phase_genes.arrange(RIGHT, buff=self.GENOME_BUFFER).next_to(self.addition_label, RIGHT)

        self.remove(self.arrow)
        self.wait(0.25)

    def animate_deletions(self):
        self.deletion_label.set_opacity(1)

        # Make a copy of the addition phase genes for the deletion phase
        self.deletion_phase_genes = self.addition_phase_genes.copy().next_to(self.deletion_label, RIGHT)
        self.play(TransformFromCopy(self.addition_phase_genes, self.deletion_phase_genes), run_time=self.GENE_COPY_RUN_TIME)

        for index in range(len(self.deletion_phase_genes)):
            gene = cast(VMobject, self.deletion_phase_genes[index])
            self.point_to_gene(gene)
            self.play(Circumscribe(gene), run_time=self.PARENT_GENE_HIGHLIGHT_RUN_TIME)

            delete_here = random.random() < self.DELETION_RATE
            if delete_here:
                deleted_gene = gene.copy()
                deleted_gene.set_opacity(0.25)
                self.play(Transform(gene, deleted_gene))
                pass

        self.remove(self.arrow)
        self.wait(0.25)

    def build_labels_and_initial_genome(self) -> tuple[VGroup, Text, Text, Text]:
        """
        Builds the parent, addition, and deletion labels, and the parent child genome mobject.

        This method creates the visual representations of the initial genome and all three labels,
        arranges them, but does not add them to the scene.

        Returns:
            A tuple containing the mobjects for parent genes and the three labels.
        """
        parent_label: Text = Text("Parent genes", font_size=self.LABEL_FONT_SIZE)
        addition_label: Text = Text("Addition", font_size=self.LABEL_FONT_SIZE).set_opacity(0)
        deletion_label: Text = Text("Deletion", font_size=self.LABEL_FONT_SIZE).set_opacity(0)
        VGroup(parent_label, addition_label, deletion_label).arrange(DOWN, buff=self.GENOMES_VERTICAL_BUFFER)
        # Right aligns all the labels
        addition_label.align_to(parent_label, RIGHT)
        deletion_label.align_to(parent_label, RIGHT)

        parent_genes: VGroup = self.build_genome(self.PARENT_GENE_COLOR, self.PARENT_STROKE_COLOR).next_to(parent_label, RIGHT, buff=self.LABEL_BUFFER)

        return parent_genes, parent_label, addition_label, deletion_label

    def build_genome(self, fill_color: ManimColor, stroke_color: ManimColor) -> VGroup:
        """Builds a single genome as a VGroup of squares."""
        return VGroup(*[
            self.build_gene(fill_color, stroke_color, i)
            for i in range(self.GENOME_LENGTH)
        ]).arrange(RIGHT, buff=self.GENOME_BUFFER)

    def build_gene(self, fill_color: ManimColor, stroke_color: ManimColor,
                   index: int,
                   parent_direction: Optional[Side] = None,
                   label: Optional[VMobject] = None):
        result = VGroup() # create a VGroup
        box = Square(
            side_length=self.GENE_SIDE_LENGTH, fill_color=fill_color, fill_opacity=self.GENE_FILL_OPACITY,
            stroke_color=stroke_color, stroke_width=self.GENE_STROKE_WIDTH
        )
        char_text = chr(index + ord('a'))
        suffix = "" if parent_direction is None else "_c"
        if label:
            text = label.move_to(box.get_center())
        else:
            text = MathTex(f"{char_text}{suffix}", font_size=self.GENE_FONT_SIZE).move_to(box.get_center()) # create text
        result.add(box, text) # add both objects to the VGroup
        if parent_direction != None:
            direction = 1 if parent_direction == Side.LEFT else -1
            arrow = Arrow(
                start=direction * 0.5 * self.CHILD_ARROW_LENGTH * LEFT,
                  end=direction * 0.5 * self.CHILD_ARROW_LENGTH * RIGHT,
                  color=self.CROSSOVER_LINE_COLOR,
                  max_tip_length_to_length_ratio=0.5,
                  max_stroke_width_to_length_ratio=10
                ).align_to(box, UP).shift(DOWN * 0.05).align_to(box, RIGHT * direction).shift(RIGHT * 0.1 * direction)
            result.add(arrow)
        return result

    def point_to_gene(self, gene: Mobject):
        self.play(self.arrow.animate.next_to(gene, UP), run_time=self.ARROW_RUN_TIME)
