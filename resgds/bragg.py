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
    def __init__(self,width, gap, length, cell, radius=0, layer=0):
        self.__width = width
        self.__gap = gap
        self.__length = length
        self.__cell = cell
        self.__radius = radius
        self.__layer = layer
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

    def mirror(self, x0, y0):
        """
            Defines a quarterwave Bragg mirror section.
        """
        coords = lambda x,dx=0: x+dx
        wc = 8.11 # Conductor width of cavity
        gc = 17.85 # Gap b/w conductor and substrate
        rm_width = 4*wc + 2*gc
        l1, l2, l3, arc = self.section_lengths(wc,gc)
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
        xrm0, yrm0 = [coords(x0-rm_width/2 + wc/2+gc),coords(y0)]
        remove = BuildRect(self.__cell,rm_width, l1, layer = self.__layer+1)
        bragg_remove = remove.make(xrm0,yrm0,layer= self.__layer+1) 

        #print(rm_width)
        xrm1, yrm1 = [coords(x2-rm_width/2 + wc/2+gc),coords(y2)]
        remove = BuildRect(self.__cell,rm_width, l2, layer = self.__layer+1)
        bragg_remove += remove.make(xrm1,yrm1,layer= self.__layer+1)

        xrm2, yrm2 = [coords(x4-rm_width/2 + wc/2+gc),coords(y4)]
        remove = BuildRect(self.__cell,rm_width, l3, layer = self.__layer+1)
        bragg_remove += remove.make(xrm2,yrm2,layer= self.__layer+1)

        arcrad = 2*gc+wc
        xhf0, yhf0 = [coords(xrm0 + rm_width + arcrad),(yrm0 + l1)]
        bragg_remove += rs.make_halfarc(arcrad, rm_width , 
            xhf0, yhf0, orientation='N', npoints=40,layer=3)
        
        xhf1, yhf1 = [coords(xrm1 + rm_width + arcrad),(yhf0 - l2)]
        bragg_remove += rs.make_halfarc(arcrad, rm_width,  
            xhf1, yhf1, orientation='S', npoints=40,layer=3)
###################################################################################
        self.__xstrt = x1
        self.__xstop = x4
        self.__ystrt = y1
        self.__ystop = y4 + l3

        return bragg

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

    def rotate_mirror2(self, x0, y0):
        """
            Defines a quarterwave Bragg mirror section.
        """
        coords = lambda x,dx=0: x+dx

        rs = Shapes(self.__cell)

        wc = 8.11 # Conductor width of cavity
        gc = 17.85 # Gap b/w conductor and substrate
        lc = 8108.45 # Length of cavity

        wlow = 30.44  # Width of low impedance section
        glow = .5*(wc + 2*gc - wlow) # Gap of low impedance section
        llow = 4051.32 # Length of low impedance section

        whigh = 2 #·
        ghigh = .5*(wlow + 2*glow - whigh)
        lhigh = 4051.32
        
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

        self.__mirror.straight_trench(l1, x0, y0-l1, orient='V')

        rm_width = 4*wc + 2*gc
        remove = BuildRect(self.__cell,rm_width, l1, layer = self.__layer+1)
        rms1 = remove.make(x0-rm_width/2 + wc/2+gc,y0-l1,layer= self.__layer+1) 

        x1,y1 = [coords(x0,self.__width+2*self.__gap+self.__radius), coords(y0,-l1)]
        self.__mirror.halfarc_trench(self.__radius, x1, y1, orient='S', npoints=40)

        x2,y2 = [coords(x1,self.__radius), coords(y1)]
        self.__mirror.straight_trench(l2,x2,y2,orient='V')

        remove = BuildRect(self.__cell,rm_width, l2, layer = self.__layer+1)
        rms2 = remove.make(x2-rm_width/2 + wc/2+gc,y2,layer= self.__layer+1)

        x3,y3 = [coords(x2,self.__width+2*self.__gap+self.__radius), coords(y2,l2)]
        self.__mirror.halfarc_trench(self.__radius, x3, y3, orient='N', npoints=40)

        x4,y4 = [coords(x3,self.__radius), coords(y3,-l3)] 
        self.__mirror.straight_trench(l3,x4,y4,orient='V')

        remove = BuildRect(self.__cell,rm_width, l3, layer = self.__layer+1)
        rms3 = remove.make(x4-rm_width/2 + wc/2+gc,y4,layer= self.__layer+1)

        wdth = rms2[0][0] - rms1[0][0]
        wdth2 = -1*(wdth/2 + rm_width/2)
        rhf1 = rs.make_halfarc(0, wdth2, rms2[1][0] + wdth2/2 - 55.5, y1, orientation='N', npoints=40,layer=3)

        wdth2 = -1*(wdth/2 + rm_width/2)
        rhf1 = rs.make_halfarc(0, wdth2, rms3[1][0] + wdth2/2 - 55.5, y1+l2, orientation='S', npoints=40,layer=3)

        self.__xstrtr = x1
        self.__xstopr = x4
        self.__ystrtr = y1
        self.__ystopr = y4

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

