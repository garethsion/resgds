#!/usr/bin/env python

import numpy as np
from resgds import *

class Bragg:
    def __init__(self,width, gap, length, cell, radius=0, layer=0):
        self.__width = width
        self.__gap = gap
        self.__length = length
        self.__cell = cell
        self.__radius = radius
        self.__layer = layer
        self.__mirror = Trench(self.__width,
                self.__gap,self.__cell,self.__layer)
        return

    def mirror(self, x0, y0):
        """ 
            Defines a quarterwave Bragg mirror section.
        """
        coords = lambda x,dx=0: x+dx
        l1, l2, l3 = self.section_lengths()
                
        self.__mirror.straight_trench(l1, x0, y0, orient='V')

        x1,y1 = [coords(x0,self.__width+2*self.__gap+self.__radius), coords(y0,l1)]
        self.__mirror.halfarc_trench(self.__radius, x1, y1, orient='N', npoints=40)

        x2,y2 = [coords(x1,self.__radius), coords(y1,-l2)]
        self.__mirror.straight_trench(l2,x2,y2,orient='V')
        
        x3,y3 = [coords(x2,self.__width+2*self.__gap+self.__radius), coords(y2)]
        self.__mirror.halfarc_trench(self.__radius, x3, y3, orient='S', npoints=40)
        
        x4,y4 = [coords(x3,self.__radius), coords(y3)] 
        self.__mirror.straight_trench(l3,x4,y4,orient='V')

    def section_lengths(self):
        r1 = self.__radius
        r2 = r1 + self.__gap
        r3 = r2 + self.__width

        al1,al2,al3 = [np.pi*r1, np.pi*r2, np.pi*r3]
        arclength = al3 - al2 -al1
        remain_length = self.__length - 2*arclength

        l1,l2,l3 = [remain_length/6, remain_length/2, remain_length/3]
        return l1, l2, l3

    def mirror_width(self):
        width = 2*(self.__width + 2*self.__gap + 2*self.__radius)
        return width

    def join_mirrors(self):
        return
