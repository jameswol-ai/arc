import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class Building3DExtrusion:
    """
    Generates a structurally aligned 3D building massing
    from grid + columns + floors.
    """

    def __init__(self, width, depth, floor_height, floors, grid, columns):
        self.width = width
        self.depth = depth
        self.floor_height = floor_height
        self.floors = floors
        self.grid = grid
        self.columns = columns

    def draw(self):

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection="3d")

        # -------------------------------------------------
        # 1. FLOOR SLABS (EXTRUSION)
        # -------------------------------------------------
        for f in range(self.floors):

            z = f * self.floor_height

            ax.bar3d(
                0,
                0,
                z,
                self.width,
                self.depth,
                self.floor_height * 0.9,
                alpha=0.15,
                shade=True
            )

        # -------------------------------------------------
        # 2. STRUCTURAL COLUMNS (VERTICAL ALIGNMENT)
        # -------------------------------------------------
        for (x, y), col in self.columns.items():

            z_bottom = 0
            z_top = self.floors * self.floor_height

            ax.plot(
                [x, x],
                [y, y],
                [z_bottom, z_top],
                color="black",
                linewidth=1.2
            )

        # -------------------------------------------------
        # 3. STRUCTURAL GRID (GROUND LEVEL ONLY)
        # -------------------------------------------------
        for x in self.grid.x_lines:
            ax.plot(
                [x, x],
                [0, self.depth],
                [0, 0],
                color="gray",
                linewidth=0.5
            )

        for y in self.grid.y_lines:
            ax.plot(
                [0, self.width],
                [y, y],
                [0, 0],
                color="gray",
                linewidth=0.5
            )

        # -------------------------------------------------
        # 4. VISUAL SETTINGS
        # -------------------------------------------------
        ax.set_title("3D Structural Extrusion (Aligned System)")

        ax.set_xlabel("Width")
        ax.set_ylabel("Depth")
        ax.set_zlabel("Height")

        ax.view_init(elev=25, azim=35)

        return fig
