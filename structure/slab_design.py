class Slab:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.thickness = 0.2
        self.load = 0


class SlabSystem:
    def __init__(self, grid, columns):
        self.grid = grid
        self.columns = columns
        self.slabs = []

    def generate_slabs(self):
        nodes = self.grid.get_nodes()
        spacing = self.grid.spacing

        for x, y in nodes:

            # only create slab if surrounded by columns
            self.slabs.append(
                Slab(x, y, spacing)
            )

        return self.slabs
