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


    # def straight(self, l, w, gap, x0, y0, orientation):
    #     """
    #     Defines a straight conductor surrounded by two gap sections
    #     """
    #     if orientation == 'H':
    #         return [self.rect(l, gap, x0, y0), self.rect(l, gap, x0, y0 + gap + w)]
    #     if orientation == 'V':
    #         return [self.rect(gap, l, x0, y0), self.rect(gap, l, x0 + gap + w, y0)]

    def straight_trench(self, l, w, gap, x0, y0, orientation):
        """
        Defines a straight conductor surrounded by two gap sections
        """
        if orientation == 'H':
            return [self.rect(l, gap, x0, y0), self.rect(l, gap, x0, y0 + gap + w)]
        if orientation == 'V':
            return [self.rect(gap, l, x0, y0), self.rect(gap, l, x0 + gap + w, y0)]

    def thinning_trench(self,w1, w2, rat, x0, y0, H, orientation = 'H', strait=[0]):
        '''
        list of list of tuples
        '''
        w1 = float(w1)
        w2 = float(w2)

        stl = strait
        print(strait)
        print('\n')
        print(stl[0][0][1])

        if(orientation=='N'):
            d1 = [(stl[0][1][0], stl[0][0][1]), (stl[0][0][0], stl[0][0][1]),
             (x0, y0), (x0+w1*rat, y0)]
            d2 = [(stl[1][1][0], stl[1][0][1]), (stl[1][0][0], stl[1][0][1]),
             (x0+2*H-w1*rat, y0), (x0+2*H, y0)]

        elif(orientation == 'E'):
            d1 = [(x0, y0), (x0, y0 - w1*rat), (stl[1][1][0], stl[1][1][1]), 
                (stl[1][1][0], stl[1][2][1])]
            d2 = [(x0, y0 - w1*(1 + rat)), (x0, y0 - w1*(1 + 2*rat)), 
            (stl[0][1][0], stl[0][1][1]), (stl[0][1][0], stl[0][2][1])]

        elif(orientation == 'W'):
            d1 = [(x0, y0), (x0, y0 - w1*rat), (stl[0][3][0], stl[1][0][1]), 
                (stl[0][3][0], stl[1][3][1])]
            d2 = [(x0, y0 - w1*(1 + rat)), (x0, y0 - w1*(1 + 2*rat)), 
            (stl[0][3][0], stl[0][0][1]), (stl[0][3][0], stl[0][3][1])]
        return [d1, d2]

    def make_halfarc(self, r, w, x0, y0, orientation='E', npoints=40,layer=0):
        slist = self.halfarc(r, w,x0,y0,orientation=orientation,npoints=npoints)
        l1 = gdspy.Polygon(slist,layer)
        #l2 = gdspy.Polygon(slist[1],layer)
        
        self.__cell.add(l1)
        #self.__cell.add(l2)
        return slist

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

    def straight_trench(self,length, x0, y0, orient='H'):
        trench_list = super().straight_trench(length, 
                self.__width, self.__gap, x0, y0, orient)
        t1 = gdspy.Polygon(trench_list[0],self.__layer)
        t2 = gdspy.Polygon(trench_list[1],self.__layer)
        self.__cell.add(t1)
        self.__cell.add(t2)
        return trench_list

    def quarterarc_trench(self, r, x0, y0, orient='NE', npoints=20):
        trench_list = super().quarterarc_trench(r, self.__width,
                self.__gap,x0,y0,orient=orient,npoints=npoints)
        t1 = gdspy.Polygon(trench_list[0],self.__layer)
        t2 = gdspy.Polygon(trench_list[1],self.__layer)
        self.__cell.add(t1)
        self.__cell.add(t2)
        return trench_list

    def halfarc_trench(self, r, x0, y0, orient='E', npoints=40):
        trench_list = super().halfarc_trench(r, self.__width,
                self.__gap,x0,y0,orient=orient,npoints=npoints)

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
    
    def straight_trench(self,length, x0, y0, orient='H'):
        trench_list = super().straight_trench(length, 
                self.__width, self.__gap, x0, y0, orient)
        t1 = gdspy.Polygon(trench_list[0],self.__layer)
        t2 = gdspy.Polygon(trench_list[1],self.__layer)
        self.__cell.add(t1)
        self.__cell.add(t2)
        return trench_list
    
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
        return dots


    def feedbond(self,feedlength,cc,rat,bond,x0,y0,orientation='N'): 
        w1 = bond
        w2 = cc
        H = bond
        
        # w = H*rat
        # l = H*(1 + 2*rat)
        x0_rect = x0
        y0_rect = y0 - H + cc/2

        if(orientation=='N' or orientation=='S'):
            straight_orient = 'V'
            xstrt = self.__xbound - H/2
            w = H*(1 + 2*rat)
            l = H*rat
        elif(orientation=='E'):
            straight_orient = 'H'
            xstrt = self.__xbound - H/2
            w = H*rat
            l = H*(1 + 2*rat)
        elif(orientation=='W'):
            straight_orient = 'H'
            xstrt = self.__xbound
            w = H*rat
            l = H*(1 + 2*rat)

        #straight = self.straight_trench(feedlength, x0, y0-w, straight_orient)
        straight = self.straight_trench(feedlength, x0, y0-feedlength, straight_orient)
        #feed = [self.rect(w,l, self.__xbound-H/2, y0_rect)]
        feed = [self.rect(w,l, self.__xbound-H/2, y0_rect-300)]
        print(feed)
        feed += self.thinning_trench(w1, w2, rat, feed[0][3][0], feed[0][3][1], 
                H, orientation,straight)
        #feed += self.thinning_trench(w1, w2, rat, xstrt, y0_rect+l, 
        #        H, orientation,straight)         
        return feed

    def make_feedbond(self,feedlength,cc,rat,bond, x0, y0, orientation='N'):
        feedbond = self.feedbond(feedlength,cc,rat,bond,x0, y0, orientation)
        for i in feedbond:
            self.__cell.add(gdspy.Polygon(i, self.__layer))    
        return feedbond

class Quarterwave(Shapes):
    def __init__(self):
        super().__init__()
        return

class Halfwave(Shapes):
    def __init__(self):
        super().__init__()
        return
