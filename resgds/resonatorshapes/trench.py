#!/usr/bin/env python

"""
    This program contains the class which allows for defining the gds patterns
"""

import numpy as np
import gdspy
from resgds.resonatorshapes import Shapes
    
class Trench():
    def __init__(self, width, gap, cell, layer=0):
        self.__width = width
        self.__gap = gap
        self.__layer = layer
        self.__cell = cell
        self.__rs = Shapes(self.__cell)
        return

    def straight_trench(self,length, x0, y0, orient='H'):
        trench_list = self.__rs.straight_trench(length, 
                self.__width, self.__gap, x0, y0, orient)
        t1 = gdspy.Polygon(trench_list[0],self.__layer)
        t2 = gdspy.Polygon(trench_list[1],self.__layer)
        self.__cell.add(t1)
        self.__cell.add(t2)
        return trench_list

    def thinning_trench(self,w1, w2, rat, x0, y0, H, orientation='N', strait=[0]):
        trench_list = self.__rs.thinning_trench(w1, w2, rat, x0, y0, H, orientation, strait)
        t1 = gdspy.Polygon(trench_list[0],self.__layer)
        t2 = gdspy.Polygon(trench_list[1],self.__layer)
        self.__cell.add(t1)
        self.__cell.add(t2)
        return trench_list

    def taper(self,w1,g1,w2,g2,x0,y0,x1,y1):
        trench_list = self.__rs.taper(w1,g1,w2,g2,x0,y0,x1,y1)
        t1 = gdspy.Polygon(trench_list[0],self.__layer)
        t2 = gdspy.Polygon(trench_list[1],self.__layer)
        self.__cell.add(t1)
        self.__cell.add(t2)
        return trench_list

    def quarterarc_trench(self, r, x0, y0, orient='NE', npoints=20):
        trench_list = self.__rs.quarterarc_trench(r, self.__width,
                self.__gap,x0,y0,orient=orient,npoints=npoints)
        t1 = gdspy.Polygon(trench_list[0],self.__layer)
        t2 = gdspy.Polygon(trench_list[1],self.__layer)
        self.__cell.add(t1)
        self.__cell.add(t2)
        return trench_list

    def halfarc_trench(self, r, x0, y0, orient='E', npoints=40):
        trench_list = self.__rs.halfarc_trench(r, self.__width,
                self.__gap,x0,y0,orient=orient,npoints=npoints)

        t1 = gdspy.Polygon(trench_list[0],self.__layer)
        t2 = gdspy.Polygon(trench_list[1],self.__layer)
        self.__cell.add(t1)
        self.__cell.add(t2)
        return trench_list
