import math
from typing import List, Tuple


class GammaClass:
    def __init__(self):
        # does nothing
        pass

    def getpivalue(self) -> float:
        """
        Returns the value of pi.
        """
        return math.pi

    def getcirclearea(self, radius: float) -> float:
        """
        Returns the area of a circle given its radius.
        """
        return math.pi * (radius**2)

    def getcirclecircumference(self, radius: float) -> float:
        """
        Returns the circumference of a circle given its radius.
        """
        return 2 * math.pi * radius
