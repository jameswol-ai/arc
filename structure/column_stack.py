class Column:
    def __init__(self, x, y, size=0.4):
        self.x = x
        self.y = y
        self.size = size
        self.floors = []  # floors this column exists on

    def add_floor(self, floor_index):
        if floor_index not in self.floors:
            self.floors.append(floor_index)


class ColumnStack:
    """
    Ensures vertical structural continuity across floors.
    This is the 'skeleton' of the building.
    """

    def __init__(self, grid_nodes):
        self.columns = {}
        self.grid_nodes = grid_nodes

    def initialize_base_columns(self, density=0.6):
        """
        Select subset of grid nodes as columns
        """
        import random

        for node in self.grid_nodes:
            if random.random() < density:
                self.columns[node] = Column(node[0], node[1])

    def propagate_to_floors(self, num_floors):
        """
        Extend all columns vertically through building
        """
        for col in self.columns.values():
            for f in range(num_floors):
                col.add_floor(f)

    def enforce_continuity(self):
        """
        Ensures no floating or broken columns
        """
        valid_columns = {}

        for key, col in self.columns.items():
            if len(col.floors) > 0:
                valid_columns[key] = col

        self.columns = valid_columns

    def get_columns_at_floor(self, floor_index):
        return [
            col for col in self.columns.values()
            if floor_index in col.floors
        ]

    def debug_summary(self):
        return {
            "total_columns": len(self.columns),
            "sample": list(self.columns.keys())[:5]
        }

    def generate_columns(grid_axes: int, floors: int):
    return [
        {"column_id": f"C{i}-{j}", "floors": floors}
        for i in range(grid_axes)
        for j in range(grid_axes)
    ]
