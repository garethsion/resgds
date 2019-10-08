#!/usr/bin/env python

"""
    This program contains the class which allows for defining the gds patterns
"""

import numpy as np
import gdspy
from resgds.resonatorshapes import Shapes

class BuildRect():
    def __init__(self, cell, w, l, layer=0):
        self.__cell = cell
        self.__rs = Shapes(self.__cell)
        self.__w = w
        self.__l = l 
        self.__layer = layer
        return

    def make(self, x0, y0, layer=0):
        rectangle = self.__rs.rect(self.__w, self.__l, x0, y0)
        rec = gdspy.Polygon(rectangle,layer)
        self.__cell.add(rec)
        return rectangle

