class LoadPathEngine:
    """
    Traces how loads travel:
    slab → beam → column → foundation
    """

    def __init__(self, slabs, beams, columns):
        self.slabs = slabs
        self.beams = beams
        self.columns = columns

    def distribute_loads(self, live_load=3.0, dead_load=5.0):

        total_load = live_load + dead_load

        for slab in self.slabs:
            slab.load = total_load

        # distribute to beams
        for beam in self.beams:
            beam.shear = total_load * 0.5
            beam.moment = beam.shear * beam.length / 4

        # distribute to columns
        for col in self.columns.values():
            col.load = sum(
                b.shear for b in self.beams
                if b.start == (col.x, col.y) or b.end == (col.x, col.y)
            )

    def check_failures(self):
        failures = []

        for col in self.columns.values():
            if getattr(col, "load", 0) > 1000:
                failures.append(("COLUMN_OVERLOAD", col.x, col.y))

        for beam in self.beams:
            if beam.moment > 200:
                failures.append(("BEAM_FAIL", beam.start, beam.end))

        return failures
