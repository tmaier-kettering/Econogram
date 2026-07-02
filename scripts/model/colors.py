"""Color assignment for cash flow series.

Ported from the ColorManager class that used to live in
scripts/Final_CFD.py, with one fix: the fallback generator (used once the
20-color base palette is exhausted) now actually checks its candidate
against colors already in use and perturbs until it finds a free one,
instead of assuming golden-ratio hue spacing can't collide.
"""
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


class ColorAssigner:
    """Assigns and recycles colors for cash flow series."""

    def __init__(self):
        self.base_colors = list(plt.colormaps["tab20"].colors)
        self.available_colors = self.base_colors.copy()
        self.used_colors = set()

    def get_color(self):
        """Return a color not currently in use."""
        if self.available_colors:
            color = self.available_colors.pop(0)
        else:
            color = self._generate_new_color()
        self.used_colors.add(color)
        return color

    def return_color(self, color):
        """Return a color to the available pool when a series is deleted.
        Inserted at the front (not appended) so a just-freed color is the
        next one reused, rather than sitting behind the remaining base
        palette queue until it's exhausted."""
        if color in self.used_colors:
            self.used_colors.remove(color)
            if color not in self.available_colors:
                self.available_colors.insert(0, color)

    def return_colors_not_in_use(self, colors_in_use: set):
        """Free any currently-tracked color that isn't in `colors_in_use`."""
        if not colors_in_use:
            self.available_colors = self.base_colors.copy()
            self.used_colors.clear()
            return
        for color in list(self.used_colors):
            if color not in colors_in_use:
                self.return_color(color)

    def reset(self):
        self.available_colors = self.base_colors.copy()
        self.used_colors.clear()

    def _generate_new_color(self):
        """Generate a color not already in `used_colors`.

        Starts from a golden-ratio hue step (good distribution in the
        common case), but actually verifies uniqueness and perturbs the
        saturation/value on collision instead of assuming one can't
        happen.
        """
        attempt = len(self.used_colors) - len(self.base_colors)
        while True:
            hue = (attempt * 0.618033988749895) % 1.0
            saturation = 0.6 + (attempt % 3) * 0.15
            value = 0.7 + (attempt % 2) * 0.2
            rgb = tuple(mcolors.hsv_to_rgb([hue, saturation, value]))
            if rgb not in self.used_colors:
                return rgb
            attempt += 1
