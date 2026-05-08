class Beam:
    def __init__(self, start, end, depth=0.6):
        self.start = start
        self.end = end
        self.depth = depth

        self.length = ((end[0]-start[0])**2 + (end[1]-start[1])**2) ** 0.5

        self.moment = 0
        self.shear = 0


class BeamSystem:
    """
    Connects column nodes into structural spans.
    """

    def __init__(self, columns, grid_spacing):
        self.columns = columns
        self.grid_spacing = grid_spacing
        self.beams = []

    def generate_beams(self):
        points = list(self.columns.keys())

        for p1 in points:
            for p2 in points:

                if p1 == p2:
                    continue

                # only connect orthogonal neighbors
                dx = abs(p1[0] - p2[0])
                dy = abs(p1[1] - p2[1])

                if (dx == self.grid_spacing and dy == 0) or \
                   (dy == self.grid_spacing and dx == 0):

                    self.beams.append(Beam(p1, p2))

        return self.beams
