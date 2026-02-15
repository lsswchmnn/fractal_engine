
#============================================================
class ColorMap():
    def __init__(self):
        self.colormap : list = []
        self.iteration = None    # Wie Iterationsregel definieren?

    def define_colormap(points:int=3) -> list:
        new_map = []
        for point in points:
            pass