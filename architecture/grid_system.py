import numpy as np

class StructuralGrid:
    """
    Generates a structural grid for building layout.
    Columns, beams, and rooms snap to this system.
    """

    def __init__(self, width, depth, spacing=6):
        self.width = width
        self.depth = depth
        self.spacing = spacing

        self.x_lines = []
        self.y_lines = []
        self.nodes = []

        self._generate_grid()

    def _generate_grid(self):
        self.x_lines = np.arange(0, self.width + self.spacing, self.spacing)
        self.y_lines = np.arange(0, self.depth + self.spacing, self.spacing)

        # intersection nodes = potential column positions
        self.nodes = [
            (x, y)
            for x in self.x_lines
            for y in self.y_lines
        ]

    def get_nodes(self):
        return self.nodes

    def get_bay_size(self):
        return self.spacing

    def snap_to_grid(self, x, y):
        """Snap any coordinate to nearest structural node"""
        snapped_x = min(self.x_lines, key=lambda v: abs(v - x))
        snapped_y = min(self.y_lines, key=lambda v: abs(v - y))
        return snapped_x, snapped_y

    def visualize_grid(self, ax):
        """Optional matplotlib helper"""
        for x in self.x_lines:
            ax.plot([x, x], [0, self.depth], linewidth=0.5, color="gray")

        for y in self.y_lines:
            ax.plot([0, self.width], [y, y], linewidth=0.5, color="gray")
