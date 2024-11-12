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

    def triangle(self,x0,y0,x1,y1,x2,y2,x3,y3):
        return[(x0,y0),(x1,y1),(x2,y2),(x3,y3)]
    
    def right_angle_triangle(self, x0, y0, x1, y1):
        return[(x0,y0),(x0,y1),(x1,y0)]
    
    def three_triangle(self, x0, y0, x1, y1, x2, y2):
        return[(x0,y0), (x1,y1), (x2,y2)]
        


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

    def exptaper(self):
        d1 = [(x0, y0), (x0 + g1, y0),(x0+g2,y1),(x0, y1)]
        d2 = [(x0 + w1 + g1, y0), (x0 + w1 + 2*g1, y0), (x0 + w2 + 2*g2, y1),(x0 + w2 + g2, y1)]

    def exptaper(self,w1,w2,L,x0,npoints=100):
    
        x = np.linspace(x0,x0+L,npoints)
        # print(x)

        curve1 = np.zeros(len(x))
        curve2 = np.zeros(len(x))

        for i in range(0,len(x)):
            curve1[i] = w1*np.exp((x[i]/L * np.log(w2/w1)))
            curve2[i] = -1*w1*np.exp((x[i]/L * np.log(w2/w1)))
                
        x0 = x[0], x[0]
        y0 = curve1[0], curve2[0]

        taper = [ list(zip(x0,y0)) ]

        x1 = list(x) 
        y1 = list(curve1)
        taper += [ list(zip(x1,y1)) ]

        x2 = x[len(x)-1], x[len(x)-1] 
        y2 = curve1[len(x)-1], curve2[len(x)-1] 
        taper += [ list(zip(x2,y2)) ]
        
        x3 =  x 
        y3 =  curve2
        taper += [ list(zip(x3,y3)) ]
        
        return taper

    def feedline(cc, rat, r, W, H, bond, d_dots):
        #deltaL
        dL = [rect(bond*(1 + 2*rat), bond*rat, 0, 0)]
        dL += straight_trench(bond, bond*rat, bond, 0, bond*rat, orientation='V')
        dL += thinning_trench_style_2(bond, cc, rat, 0, bond*(1+rat), bond)

        #deltaR
        dR = [rect(bond*(1 + 2*rat), bond*rat, cc*(1 + 2*rat) + W + 2*r, 0)]
        dR += straight_trench(bond, bond*rat, bond, cc*(1 + 2*rat) + W + 2*r, bond*rat, orientation='V')
        dR += thinning_trench_style_2(bond, cc, rat, cc*(1 + 2*rat) + W + 2*r, bond*(1+rat), bond)

        #narrow - shapes start on left and move along feedline
        narrow = straight_trench(H, cc*rat, cc, bond*(rat + .5) - cc*(rat + .5), bond*(2 + rat), orientation='V')
        narrow += quarterarc_trench(r, cc, cc*rat, r+ bond*(rat + .5) + cc*(rat + .5), bond*(2 + rat) + H, orient='NW')
        narrow += straight_trench(W, cc*rat, cc, r+ bond*(rat + .5) + cc*(rat + .5), bond*(2 + rat) + H + r, orientation='H')
        narrow += quarterarc_trench(r, cc, cc*rat, r+ W + bond*(rat + .5) + cc*(rat + .5) , bond*(2 + rat) + H, orient='NE')
        narrow += straight_trench(H, cc*rat, cc, bond*(rat + .5) + cc*(rat + .5) + W + 2*r, bond*(2 + rat), orientation='V')

        #shapes to remove antidots from
        #dl
        remove = [rect(bond*(1 + 2*rat) + 2*d_dots, bond*(rat + 1) + d_dots, -d_dots , -d_dots)]
        remove += [[(-d_dots, bond*(rat + 1)), (bond*(1 + 2*rat) + d_dots, bond*(rat + 1)), (bond*(rat + .5) + cc*(rat + .5) + d_dots, bond*(rat + 2)), (bond*(rat + .5) - cc*(rat + .5) - d_dots, bond*(rat + 2))]]

        #dr
        remove += [rect(bond*(1 + 2*rat) + 2*d_dots,  bond*(rat + 1) + d_dots, cc*(1 + 2*rat) + W + 2*r -d_dots, -d_dots)]
        remove += [[(cc*(1 + 2*rat) + W + 2*r - d_dots, bond*(rat + 1)), (d_dots + cc*(1 + 2*rat) + W + 2*r + bond*(1 + 2*rat), bond*(rat + 1)), (d_dots + cc*(1 + 2*rat) + W + 2*r + bond*(rat + .5) + cc*(rat + .5), bond*(rat + 2)), (cc*(1 + 2*rat) + W + 2*r +bond*(rat + .5) - cc*(rat + .5) - d_dots, bond*(rat + 2))]]

        #narrow quarterarc(r, w, x0, y0, orientation='NE')
        remove += [rect(cc*(1 + 2*rat) + 2*d_dots, H, bond*(rat + .5) - cc*(rat + .5) - d_dots, bond*(2 + rat))]
        remove += [quarterarc(r - d_dots, cc*(1 + 2*rat) + 2*d_dots, r+ bond*(rat + .5) + cc*(rat + .5), bond*(2 + rat) + H, orientation='NW')]
        remove += [rect(W, cc*(1 + 2*rat) + 2*d_dots, r+ bond*(rat + .5) + cc*(rat + .5), bond*(2 + rat) + H + r - d_dots)]
        remove += [quarterarc(r - d_dots, cc*(1 + 2*rat) + 2*d_dots, r+ W + bond*(rat + .5) + cc*(rat + .5) , bond*(2 + rat) + H, orientation='NE')]
        remove += [rect(cc*(1 + 2*rat) + 2*d_dots, H, bond*(rat + .5) + cc*(rat + .5) + W + 2*r - d_dots, bond*(2 + rat))]

        return [dL + dR + narrow, remove]

    # def exptaper(self,w1,w2,L,x0,npoints=100):
    
    #     x = np.linspace(x0,x0+L,npoints)
    #     #y = np.linspace(w1,w2,len(x))

    #     y1 = np.zeros(len(x))
    #     y2 = np.zeros(len(x))

    #     for i in range(0,len(x)-1):
    #         y1[i] = w1*np.exp(((x[i]/L) * np.log(w2/w1)))
    #         y2[i] = -1*w1*np.exp(((x[i]/L) * np.log(w2/w1)))
                
    #     # taper = [ (x[0], x[0]) ]
    #     # taper += [ (y1[0], y2[0]) ]
    #     # taper += [ (x) ]
    #     taper = [ (y1) ]
    #     # taper += [ (x[len(x)-1], x[len(x)-1]) ]
    #     # taper += [ (y1[len(x)-1], y2[len(x)-1]) ]
    #     # taper += [ (list(x)) ]
    #     # taper += [ (list(y2)) ]

    #     return taper


    def taper(self,w1,g1,w2,g2,x0,y0,x1,y1):
        '''
        list of list of tuples
        '''
        
        d1 = [(x0, y0), (x0 + g1, y0),(x0+g2,y1),(x0, y1)]
        d2 = [(x0 + w1 + g1, y0), (x0 + w1 + 2*g1, y0), (x0 + w2 + 2*g2, y1),(x0 + w2 + g2, y1)]
        
        return [d1, d2]

    def thinning_trench(self,w1, w2, rat, x0, y0, H, orientation = 'N', strait=[0]):
        '''
        list of list of tuples
        '''
        w1 = float(w1)
        w2 = float(w2)

        stl = strait

        if(orientation=='N'):
            d1 = [(stl[0][1][0], stl[0][0][1]), (stl[0][0][0], stl[0][0][1]),
             (x0, y0), (x0+w1*rat, y0)]
            d2 = [(stl[1][1][0], stl[1][0][1]), (stl[1][0][0], stl[1][0][1]),
             (x0+2*H-w1*rat, y0), (x0+2*H, y0)]

        elif(orientation=='S'):
            d1 = [(stl[0][1][0], stl[0][2][1]), (stl[0][0][0], stl[0][3][1]),
             (x0, y0-H/2), (x0+w1*rat, y0-H/2)]
            
            d2 = [(stl[1][2][0], stl[1][2][1]), (stl[1][3][0], stl[1][3][1]),
             (x0+2*H-w1*rat, y0-H/2), (x0+2*H, y0-H/2)]

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

    def make_quarterarc(self, r, w, x0, y0, orientation='NE', npoints=20,layer=0):
        slist = self.quarterarc(r, w,x0,y0,orientation=orientation,npoints=npoints)
        l1 = gdspy.Polygon(slist,layer)
        #l2 = gdspy.Polygon(slist[1],layer)
        
        self.__cell.add(l1)
        #self.__cell.add(l2)
        return slist
