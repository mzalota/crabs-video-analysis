class MarkersConfiguration:
    COLOR_RED = (0, 0, 255)
    COLOR_DEEP_BLUE = (255, 0, 0)
    COLOR_GREEN = (0, 255, 0)
    COLOR_YELLOW = (0, 255, 255)
    COLOR_LIGHT_BLUE = (255, 255, 0)
    COLOR_PINK = (255, 0, 255)
    COLOR_WHITE = (255, 255, 255)


    def color_for_marker(self, marker_id):

        if marker_id == 0 or marker_id == 5:
            return self.COLOR_DEEP_BLUE

        if marker_id == 1 or marker_id == 6:
            return self.COLOR_GREEN

        if marker_id == 2 or marker_id == 7:
            return self.COLOR_YELLOW

        if marker_id == 3 or marker_id == 8:
            return self.COLOR_LIGHT_BLUE

        if marker_id == 4 or marker_id == 9:
            return self.COLOR_PINK


        return self.COLOR_WHITE