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
        """
        Defines a trench 180 degree 180 degree turn of conductor surrounded by two gap sections
        """
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
        """
        Defines a trench 90 degree 180 degree turn of conductor surrounded by two gap sections
        """
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
        """
        Defines a straight conductor surrounded by two gap sections
        """
        if orientation == 'H':
            return [self.rect(l, gap, x0, y0), self.rect(l, gap, x0, y0 + gap + w)]
        if orientation == 'V':
            return [self.rect(gap, l, x0, y0), self.rect(gap, l, x0 + gap + w, y0)]

    def thinning_trench(self,w1, w2, gap, x0, y0, orientation='V'):
        '''
        list of list of tuples
        '''
        w1 = float(w1)
        w2 = float(w2)
        if w1 > w2:
            d1 = [(x0, y0), (x0, y0 +  w1), (x0 + gap, y0 + w1), (x0 + gap + (w1 - w2)/2, y0)]
            d2 = [(x0 + w1 + 2*gap, y0), (x0 + w1 + 2*gap, y0 +  w1), (x0 + w1 + gap, y0 + w1), (x0 + gap + (w1 - w2)/2 + w2, y0)]
        else:
            d1 = [(x0, y0 - w2), (x0, y0 ), (x0 + gap + (w2 - w1)/2, y0 ), (x0 + gap , y0 - w2)]
            d2 = [(x0 + w2 + 2*gap, y0 - w2), (x0 + w2 + gap, y0 - w2), (x0 + gap + (w2 - w1)/2 + w1, y0), (x0 + w2 +2*gap, y0)]
        return [d1, d2]

    def thinning_trench_style_2(self,w1, w2, rat, x0, y0, H):
        '''
        list of list of tuples
        '''
        w1 = float(w1)
        w2 = float(w2)
        d1 = [(x0, y0), (x0 + w1*rat, y0), (x0 + w1*(rat + .5) - w2*.5, y0 + H), (x0 + w1*(rat + .5) - w2*(rat + .5), y0 + H)]
        d2 = [(x0 + w1*(1 + rat), y0), (x0 + w1*(1 + 2*rat), y0), (x0 + w1*(rat + .5) + w2*(rat + .5), y0 + H), (x0 + w1*(rat + .5) + w2*.5, y0 + H)]
        return [d1, d2]

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
   
class LayoutComponents(Shapes):
    def __init__(self,cell, x_bound, y_bound,layer=1):
        self.__xbound = x_bound
        self.__ybound = y_bound
        self.__cell = cell
        self.__layer = layer
        super().__init__(self.__cell)
        return

    def antidot_array(self,x_origin, y_origin, w, s, n):
        return [[(ii*(s + w) + x_origin, jj*(s + w) + y_origin), (ii*(s + w) 
            + w + x_origin, jj*(s + w) + y_origin),(ii*(s + w) + w + x_origin, 
                jj*(s + w) + w + y_origin), (ii*(s + w) + x_origin, jj*(s + w) 
                    + w + y_origin)]
                   for ii in np.arange(-n, self.__xbound/(s+w) + n, 1)
                   for jj in np.arange(-n, self.__ybound/(s+w) + n, 1)]

    def make_antidot_array(self,x_origin, y_origin, w, s, n):
        dots = self.antidot_array(x_origin, y_origin, w, s, n)
        for i in dots:
            self.__cell.add(gdspy.Polygon(i, self.__layer))
        return

    
    def feedline(self,cc, rat, r, W, H, bond, d_dots):

        #deltaL
        dL = [self.rect(bond*(1 + 2*rat), bond*rat, 0, 0)]
        dL += self.straight_trench(bond, bond*rat, bond, 0, bond*rat, orientation='V')
        dL += self.thinning_trench_style_2(bond, cc, rat, 0, bond*(1+rat), bond)

        #deltaR
        dR = [self.rect(bond*(1 + 2*rat), bond*rat, cc*(1 + 2*rat) + W + 2*r, 0)]
        dR += self.straight_trench(bond, bond*rat, bond, cc*(1 + 2*rat) + W + 2*r, bond*rat, orientation='V')
        dR += self.thinning_trench_style_2(bond, cc, rat, cc*(1 + 2*rat) + W + 2*r, bond*(1+rat), bond)

        #narrow - shapes start on left and move along feedline
        narrow = self.straight_trench(H, cc*rat, cc, bond*(rat + .5) - cc*(rat + .5), bond*(2 + rat), orientation='V')
        narrow += self.quarterarc_trench(r, cc, cc*rat, r+ bond*(rat + .5) + cc*(rat + .5), bond*(2 + rat) + H, orient='NW')
        narrow += self.straight_trench(W, cc*rat, cc, r+ bond*(rat + .5) + cc*(rat + .5), bond*(2 + rat) + H + r, orientation='H')
        narrow += self.quarterarc_trench(r, cc, cc*rat, r+ W + bond*(rat + .5) + cc*(rat + .5) , bond*(2 + rat) + H, orient='NE')
        narrow += self.straight_trench(H, cc*rat, cc, bond*(rat + .5) + cc*(rat + .5) + W + 2*r, bond*(2 + rat), orientation='V')

        #shapes to remove antidots from
        #dl
        remove = [self.rect(bond*(1 + 2*rat) + 2*d_dots, bond*(rat + 1) + d_dots, -d_dots , -d_dots)]
        remove += [[(-d_dots, bond*(rat + 1)), (bond*(1 + 2*rat) + d_dots, bond*(rat + 1)), (bond*(rat + .5) + cc*(rat + .5) + d_dots, bond*(rat + 2)), (bond*(rat + .5) - cc*(rat + .5) - d_dots, bond*(rat + 2))]]

        #dr
        remove += [self.rect(bond*(1 + 2*rat) + 2*d_dots,  bond*(rat + 1) + d_dots, cc*(1 + 2*rat) + W + 2*r -d_dots, -d_dots)]
        remove += [[(cc*(1 + 2*rat) + W + 2*r - d_dots, bond*(rat + 1)), (d_dots + cc*(1 + 2*rat) + W + 2*r + bond*(1 + 2*rat), bond*(rat + 1)), (d_dots + cc*(1 + 2*rat) + W + 2*r + bond*(rat + .5) + cc*(rat + .5), bond*(rat + 2)), (cc*(1 + 2*rat) + W + 2*r +bond*(rat + .5) - cc*(rat + .5) - d_dots, bond*(rat + 2))]]

        #narrow quarterarc(r, w, x0, y0, orientation='NE')
        remove += [self.rect(cc*(1 + 2*rat) + 2*d_dots, H, bond*(rat + .5) - cc*(rat + .5) - d_dots, bond*(2 + rat))]
        remove += [self.quarterarc(r - d_dots, cc*(1 + 2*rat) + 2*d_dots, r+ bond*(rat + .5) + cc*(rat + .5), bond*(2 + rat) + H, orientation='NW')]
        remove += [self.rect(W, cc*(1 + 2*rat) + 2*d_dots, r+ bond*(rat + .5) + cc*(rat + .5), bond*(2 + rat) + H + r - d_dots)]
        remove += [self.quarterarc(r - d_dots, cc*(1 + 2*rat) + 2*d_dots, r+ W + bond*(rat + .5) + cc*(rat + .5) , bond*(2 + rat) + H, orientation='NE')]
        remove += [self.rect(cc*(1 + 2*rat) + 2*d_dots, H, bond*(rat + .5) + cc*(rat + .5) + W + 2*r - d_dots, bond*(2 + rat))]

        return [dL + dR + narrow, remove]

    
class Quarterwave(Shapes):
    def __init__(self):
        super().__init__()
        return

class Halfwave(Shapes):
    def __init__(self):
        super().__init__()
        return
