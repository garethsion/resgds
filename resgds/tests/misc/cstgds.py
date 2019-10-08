#!/usr/bin/env python

"""
    This program contains the class which allows for defining the gds patterns
"""

import numpy as np
import gdspy

class Shapes:
    """
        ResGDS contains methods which allow a user to define a resonator geometry gds pattern. 
    """ 
    def __init__(self,cell):
        self.__cell = cell
        return

    def move(self,shape, dx, dy):
        return [(i[0] + dx, i[1] + dy) for i in shape]

    def flip(self,shape, axis='y'):
        if axis =='y':
            return [(i[0], -i[1]) for i in shape]
        elif axis =='x':
            return [(-i[0], i[1]) for i in shape]

    def rect(self, w, l, x0, y0):
        '''
            List of tuples
            Recangle of width and length w and l with bottom left corner at (x0, y0).
        '''
        return [(x0, y0), (x0 + w, y0), (x0 + w, y0 + l), (x0, y0 + l)]

    def straight(self, l, w, gap, x0, y0, orientation):
        """
        Defines a straight conductor surrounded by two gap sections
        """
        #return self.rect(l,w,x0,y0)
        if orientation == 'H':
        	return [self.rect(l, gap, x0, y0), self.rect(l, gap, x0, y0 + gap + w)]
        if orientation == 'V':
            return [self.rect(gap, l, x0, y0), self.rect(gap, l, x0 + gap + w, y0)]

    # def straight_trench(self, l, w, gap, x0, y0, orientation):
    #     """
    #     Defines a straight conductor surrounded by two gap sections
    #     """
    #     if orientation == 'H':
    #         return [self.rect(l, gap, x0, y0), self.rect(l, gap, x0, y0 + gap + w)]
    #     if orientation == 'V':
    #         return [self.rect(gap, l, x0, y0), self.rect(gap, l, x0 + gap + w, y0)]

class BuildRect(Shapes):
    def __init__(self, cell, w, l, layer=0):
        self.__cell = cell
        super().__init__(self.__cell)
        self.__w = w
        self.__l = l 
        self.__layer = layer
        return

    def make(self, x0, y0, layer=0):
        rectangle = self.rect(self.__w, self.__l, x0, y0)
        rec = gdspy.Polygon(rectangle,layer)
        self.__cell.add(rec)
        return rectangle
    
class Trench(Shapes):
    def __init__(self, width, gap, cell, layer=0):
        self.__width = width
        self.__gap = gap
        self.__layer = layer
        self.__cell = cell
        super().__init__(self.__cell)
        return

    def straight(self,length, x0, y0, orient='H'):
        trench_list = super().straight(length, 
                self.__width, self.__gap, x0, y0, orient)
        t1 = gdspy.Polygon(trench_list[0],self.__layer)
        t2 = gdspy.Polygon(trench_list[1],self.__layer)
        self.__cell.add(t1)
        self.__cell.add(t2)
        return trench_list
   
class LayoutComponents(Shapes):
    def __init__(self,cell, x_bound, y_bound,width = 0, gap = 0, layer=1):
        self.__xbound = x_bound
        self.__ybound = y_bound
        self.__cell = cell
        self.__layer = layer
        self.__width = width
        self.__gap = gap
        super().__init__(self.__cell)
        return
    
    def straight(self,length, x0, y0, orient='H'):
        trench_list = super().straight(length, 
                self.__width, self.__gap, x0, y0, orient)
        t1 = gdspy.Polygon(trench_list[0],self.__layer)
        #t2 = gdspy.Polygon(trench_list[1],self.__layer)
        self.__cell.add(t1)
        #self.__cell.add(t2)
        return trench_list
    
