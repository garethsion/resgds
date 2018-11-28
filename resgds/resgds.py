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

    def circ_arc(self,r, x0, y0, n=50, theta0=0, thetaf=np.pi/2):
        '''
        List of tuples giving x, y coords of a circular arc from theta_0 to theta_f
        with centre at (x0, y0) and radius r.
        '''
        return [(r*np.cos(i) + x0, r*np.sin(i) + y0)
                for i in np.linspace(theta0, thetaf, n)]

    def halfarc(self,r, w, x0, y0, orientation='E', npoints=40):
        ''' 
        List of tuples.
        A half circle trench of width w, the inner side of which is a circle with
        radius r and centre (x0, y0). Different orientations of points of compass
        with 'N' meaning that the semicircle is an arc that looks like a rainbow.
        '''
        if orientation == 'N':
            t0=0
            tf=np.pi
        elif orientation == 'E':
            t0=-np.pi/2
            tf=np.pi/2
        elif orientation == 'W':
            t0=np.pi/2
            tf=3*np.pi/2
        elif orientation == 'S':
            t0=np.pi
            tf=2*np.pi

        inner = self.circ_arc(r, x0, y0, n=npoints, theta0=t0, thetaf=tf)
        outer = self.circ_arc(r + w, x0, y0, n=npoints, theta0=t0, thetaf=tf)[::-1]

        return inner + outer

    def halfarc_trench(self,r, width, gap, x0, y0, orient='E', npoints=40):
        inside = self.halfarc(r, gap, x0, y0, orientation=orient, npoints=npoints)
        outside = self.halfarc(r + gap + width, gap, x0, y0, orientation=orient, npoints=npoints)
        return [inside, outside]
    
    def quarterarc(self, r, w, x0, y0, orientation='NE', npoints=20):
        if orientation == 'NE':
            t0=0
            tf=np.pi/2
        elif orientation == 'SE':
            t0=3*np.pi/2
            tf=2*np.pi
        elif orientation == 'SW':
            t0=np.pi
            tf=3*np.pi/2
        elif orientation == 'NW':
            t0=np.pi/2
            tf=np.pi

        inner = self.circ_arc(r, x0, y0, theta0=t0, thetaf=tf, n=npoints)
        outer = self.circ_arc(r + w, x0, y0, theta0=t0, thetaf=tf, n=npoints)[::-1]

        return inner + outer

    def quarterarc_trench(self,r, width, gap, x0, y0, orient='NE', npoints=20):
        inside = self.quarterarc(r, gap, x0, y0, orientation=orient, npoints=npoints)
        outside = self.quarterarc(r + gap + width, gap, x0, y0, orientation=orient, 
                npoints=npoints)
        return [inside, outside]

    def rect(self, w, l, x0, y0):
        '''
            List of tuples
            Recangle of width and length w and l with bottom left corner at (x0, y0).
        '''
        return [(x0, y0), (x0 + w, y0), (x0 + w, y0 + l), (x0, y0 + l)]

    def straight_trench(self, l, w, gap, x0, y0, orientation):
        if orientation == 'H':
            return [self.rect(l, gap, x0, y0), self.rect(l, gap, x0, y0 + gap + w)]
        if orientation == 'V':
            return [self.rect(gap, l, x0, y0), self.rect(gap, l, x0 + gap + w, y0)]

class BuildRect(Shapes):
    def __init__(self, cell, w, l, layer=0):
        self.__cell = cell
        super().__init__(self.__cell)
        self.__w = w
        self.__l = l 
        self.__layer = layer
        return

    def make(self, x0, y0, layer=0):
        rec = gdspy.Polygon(self.rect(self.__w, self.__l, x0, y0),layer)
        self.__cell.add(rec)
        return
    
class Trench(Shapes):
    def __init__(self, width, gap, cell, layer=0):
        self.__width = width
        self.__gap = gap
        self.__layer = layer
        self.__cell = cell
        super().__init__(self.__cell)
        return

    def straight_trench(self,length, x0, y0, orient='H'):
        trench_list = super().straight_trench(length, 
                self.__width, self.__gap, x0, y0, orient)
        t1 = gdspy.Polygon(trench_list[0],self.__layer)
        t2 = gdspy.Polygon(trench_list[1],self.__layer)
        self.__cell.add(t1)
        self.__cell.add(t2)
        return

    def quarterarc_trench(self, r, x0, y0, orient='NE', npoints=20):
        trench_list = super().quarterarc_trench(r, self.__width,
                self.__gap,x0,y0,orient=orient,npoints=npoints)
        t1 = gdspy.Polygon(trench_list[0],self.__layer)
        t2 = gdspy.Polygon(trench_list[1],self.__layer)
        self.__cell.add(t1)
        self.__cell.add(t2)
        return

    def halfarc_trench(self, r, x0, y0, orient='E', npoints=40):
        trench_list = super().halfarc_trench(r, self.__width,
                self.__gap,x0,y0,orient=orient,npoints=npoints)
        t1 = gdspy.Polygon(trench_list[0],self.__layer)
        t2 = gdspy.Polygon(trench_list[1],self.__layer)
        self.__cell.add(t1)
        self.__cell.add(t2)
        return

class Quarterwave(Shapes):
    def __init__(self):
        super().__init__()
        return

class Halfwave(Shapes):
    def __init__(self):
        super().__init__()
        return
