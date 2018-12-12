#!/usr/bin/env python

"""
This program is provides the functionality for designing the gds files for Bragg resonators. This requires the resgds library.
"""

import numpy as np
from resgds import *

class Bragg:
    """
        Contains the methods required for developing gds files for Bragg resonators
    """
    def __init__(self,width, gap, length, cell, radius=0, layer=0, remove_layer=None):
        self.__width = width
        self.__gap = gap
        self.__length = length
        self.__cell = cell
        self.__radius = radius

        self.__layer = layer
        if remove_layer:
            self.__remove_layer = self.__remove_layer
        else:
            self.__remove_layer = self.__layer + 1

        self.__mirror = Trench(self.__width,
            self.__gap,self.__cell,self.__layer)

        self.__xstrt = None
        self.__xstop = None
        self.__ystrt = None   
        self.__ystop = None
        
        self.__xstrtr = None
        self.__xstopr = None
        self.__ystrtr = None   
        self.__ystopr = None

        return

    def mirror(self, x0, y0, w_remove=0, g_remove=0):
        """
            Defines a quarterwave Bragg mirror section.
        """
        coords = lambda x,dx=0: x+dx
        rm_width = 4*w_remove + 2*g_remove
        l1, l2, l3, arc = self.section_lengths(w_remove,g_remove)
        rs = Shapes(self.__cell)

        # Make Bragg mirror sections
        #
        bragg = self.__mirror.straight_trench(l1, x0, y0, orient='V')

        x1,y1 = [coords(x0,self.__width+2*self.__gap+self.__radius), coords(y0,l1)]
        bragg += self.__mirror.halfarc_trench(self.__radius, x1, y1, orient='N', npoints=40)

        x2,y2 = [coords(x1,self.__radius), coords(y1,-l2)]
        bragg += self.__mirror.straight_trench(l2,x2,y2,orient='V')

        x3,y3 = [coords(x2,self.__width+2*self.__gap+self.__radius), coords(y2)]
        bragg += self.__mirror.halfarc_trench(self.__radius, x3, y3, orient='S', npoints=40)

        x4,y4 = [coords(x3,self.__radius), coords(y3)] 
        bragg += self.__mirror.straight_trench(l3,x4,y4,orient='V')

        # Make remove sections
        #
        xrm0, yrm0 = [coords(x0-rm_width/2 + w_remove/2+g_remove),coords(y0)]
        remove = BuildRect(self.__cell,rm_width, l1, layer=self.__remove_layer)
        bragg_remove = remove.make(xrm0,yrm0,layer=self.__remove_layer) 

        #print(rm_width)
        xrm1, yrm1 = [coords(x2-rm_width/2 + w_remove/2+g_remove),coords(y2)]
        remove = BuildRect(self.__cell,rm_width, l2, layer=self.__remove_layer)
        bragg_remove += remove.make(xrm1,yrm1,layer=self.__remove_layer)

        xrm2, yrm2 = [coords(x4-rm_width/2 + w_remove/2+g_remove),coords(y4)]
        remove = BuildRect(self.__cell,rm_width, l3, layer=self.__remove_layer)
        bragg_remove += remove.make(xrm2,yrm2,layer=self.__remove_layer)

        arcrad = .5*(2*self.__radius - g_remove - w_remove)
        xhf0, yhf0 = [coords(xrm0 + rm_width + arcrad),(yrm0 + l1)]
        bragg_remove += rs.make_halfarc(arcrad, rm_width , 
            xhf0, yhf0, orientation='N', npoints=40,layer=self.__remove_layer)
        
        xhf1, yhf1 = [coords(xrm1 + rm_width + arcrad),(yhf0 - l2)]
        bragg_remove += rs.make_halfarc(arcrad, rm_width,  
            xhf1, yhf1, orientation='S', npoints=40,layer=self.__remove_layer)

        self.__xstrt = x1
        self.__xstop = x4
        self.__ystrt = y1
        self.__ystop = y4 + l3

        return bragg, bragg_remove

    def section_lengths(self,w,g):

        out_LHS = self.__gap
        out_RHS = 2*self.__width + 3*self.__gap + 2*self.__radius 
        
        diameter = out_RHS - out_LHS - (self.__width/2)
        
        arclength = .5 * diameter * np.pi
        arctot = 2*arclength
        len_remain = self.__length - arctot

        l1 = len_remain/6
        l2 = 3*l1
        l3 = 2*l1
        return l1, l2, l3, arclength

    def rotate_mirror(self, x0, y0):
        coords = lambda x,dx=0: x+dx
        rm_width = 4*w_remove + 2*g_remove
        l1, l2, l3, arc = self.section_lengths(w_remove,g_remove)
        rs = Shapes(self.__cell)

        out_LHS = self.__gap
        out_RHS = 2*self.__width + 3*self.__gap + 2*self.__radius 
        
        diameter = out_RHS - out_LHS - (self.__width/2)
        
        arclength = .5 * diameter * np.pi
        arctot = 2*arclength
        len_remain = self.__length - arctot

        l1 = len_remain/6
        l2 = 3*l1
        l3 = 2*l1

        #l1, l2, l3 = self.section_lengths()

        self.__mirror.straight_trench(-l1, x0, y0, orient='V')

        x1,y1 = [coords(x0,-self.__radius), coords(y0,-l1)]
        self.__mirror.halfarc_trench(self.__radius, x1, y1, orient='S', npoints=40)
 
        x2,y2 = [coords(x1,-2*self.__gap - self.__width - self.__radius), coords(y1)]
        self.__mirror.straight_trench(l2,x2,y2,orient='V')

        x3,y3 = [coords(x2,-self.__radius), coords(y2,l2)]
        self.__mirror.halfarc_trench(self.__radius, x3, y3, orient='N', npoints=40)

        x4,y4 = [coords(x3,-2*self.__gap - self.__width - self.__radius), coords(y3,-l3)] 
        self.__mirror.straight_trench(l3,x4,y4,orient='V')

        self.__xstrtr = x1
        self.__xstopr = x4
        self.__ystrtr = y1
        self.__ystopr = y4# - l3

    def rotate_mirror2(self, x0, y0, w_remove=0, g_remove=0):
        """
            Defines a quarterwave Bragg mirror section.
        """
        coords = lambda x,dx=0: x+dx
        rm_width = 4*w_remove + 2*g_remove
        l1, l2, l3, arc = self.section_lengths(w_remove,g_remove)
        rs = Shapes(self.__cell)

        # Make Bragg mirror sections
        #   
        bragg = self.__mirror.straight_trench(l1, x0, y0-l1, orient='V')

        x1,y1 = [coords(x0,self.__width+2*self.__gap+self.__radius), coords(y0,-l1)]
        bragg += self.__mirror.halfarc_trench(self.__radius, x1, y1, orient='S', npoints=40)

        x2,y2 = [coords(x1,self.__radius), coords(y1)]
        bragg += self.__mirror.straight_trench(l2,x2,y2,orient='V')

        x3,y3 = [coords(x2,self.__width+2*self.__gap+self.__radius), coords(y2,l2)]
        bragg += self.__mirror.halfarc_trench(self.__radius, x3, y3, orient='N', npoints=40)

        x4,y4 = [coords(x3,self.__radius), coords(y3,-l3)]
        bragg += self.__mirror.straight_trench(l3,x4,y4,orient='V')

        # Make remove sections
        #
        xrm0, yrm0 = [coords(x0-rm_width/2 + w_remove/2+g_remove),coords(y0-l1)]
        remove = BuildRect(self.__cell,rm_width, l1, layer=self.__remove_layer)
        bragg_remove = remove.make(xrm0,yrm0,layer=self.__remove_layer)

        xrm1, yrm1 = [coords(x2-rm_width/2 + w_remove/2+g_remove),coords(y2)]
        remove = BuildRect(self.__cell,rm_width, l2, layer=self.__remove_layer)
        bragg_remove += remove.make(xrm1,yrm1,layer=self.__remove_layer)

        xrm2, yrm2 = [coords(x4-rm_width/2 + w_remove/2+g_remove),coords(y4)]
        remove = BuildRect(self.__cell,rm_width, l3, layer=self.__remove_layer)
        bragg_remove += remove.make(xrm2,yrm2,layer=self.__remove_layer)

        arcrad = .5*(2*self.__radius - g_remove - w_remove)
        xhf0, yhf0 = [coords(xrm0 + rm_width + arcrad),(yrm0)]
        bragg_remove += rs.make_halfarc(arcrad, rm_width ,
            xhf0, yhf0, orientation='S', npoints=40,layer=self.__remove_layer)

        xhf1, yhf1 = [coords(xrm1 + rm_width + arcrad),(yhf0 + l2)]
        bragg_remove += rs.make_halfarc(arcrad, rm_width,
            xhf1, yhf1, orientation='N', npoints=40,layer=self.__remove_layer)

        self.__xstrtr = x1
        self.__xstopr = x4
        self.__ystrtr = y1
        self.__ystopr = y4

        return bragg, remove

    def mirror_width(self):
        """
            Method which calculates the total width of the Bragg mirror half period 
        """
        width = 2*(self.__width + 2*self.__gap + 2*self.__radius)
        return width

    def join_mirrors(self):
        return

    def get_mirror_coordinates(self):
        coords = [(self.__xstrt, self.__ystrt),(self.__xstop, self.__ystop)]
        return coords

    def get_rotated_mirror_coordinates(self):
        coords = [(self.__xstrtr, self.__ystrtr),(self.__xstopr, self.__ystopr)]
        return coords

