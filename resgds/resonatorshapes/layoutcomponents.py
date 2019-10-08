#!/usr/bin/env python

"""
    This program contains the class which allows for defining the gds patterns
"""

import numpy as np
import gdspy
from resgds.resonatorshapes import Shapes

class LayoutComponents():
    def __init__(self,cell, x_bound, y_bound,width = 0, gap = 0, layer=1):
        self.__xbound = x_bound
        self.__ybound = y_bound
        self.__cell = cell
        self.__layer = layer
        self.__width = width
        self.__gap = gap
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


    def remove_triangle(self,feed,x0,y0):
        d = [(feed[0][0][0], y0), (feed[0][0][0]+1000, y0)]
        return d

    def feedbond_remove(self,feedlength,cc,rat,bond,x0,y0,xstr,ystr,xend,orientation):
        w1 = bond
        w2 = cc
        H = bond
        
        # w = H*rat
        # l = H*(1 + 2*rat)
        x0_rect = x0
        y0_rect = y0 - H+ cc/2

        if(orientation=='N'):
            straight_orient = 'V'
            #xstrt = self.__xbound - H/2
            w = H*(1 + 2*rat) + 50
            l = H*rat + 50
            xoff = xend-xstr
            xstrt = x0 + xoff/2
            feed_remove = [self.rect(w,l, xstrt-w/2, y0_rect-l)]
            x0t = feed_remove[0][2][0]
            y0t = feed_remove[0][2][1]
            x1t = feed_remove[0][3][0]
            y1t = feed_remove[0][3][1]
            x2t = xstr
            y2t = ystr
            x3t = xend
            y3t = ystr
        elif(orientation=='S'):
            straight_orient = 'V'
            w = H*(1 + 2*rat) + 50
            l = H*rat + 50
            xoff = xend-xstr
            xstrt = x0 + xoff/2
            feed_remove = [self.rect(w,l, xstrt-w/2, y0+H)]

            x0t = feed_remove[0][0][0]
            y0t = feed_remove[0][0][1]
            x1t = feed_remove[0][1][0]
            y1t = feed_remove[0][1][1]
            x2t = xend
            y2t = ystr
            x3t = xstr
            y3t = ystr
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

        feed_remove += [self.triangle(x0t,y0t,x1t,y1t,x2t,y2t,x3t,y3t)]
        return feed_remove

    def feedbond(self,feedlength,cc,rat,bond,x0,y0,orientation='N'): 
        w1 = bond
        w2 = cc
        H = bond
        
        # w = H*rat
        # l = H*(1 + 2*rat)
        x0_rect = x0
        y0_rect = y0 - H + cc/2

        xstrt = self.__xbound - H/2
        xoff = self.__xbound - x0
        xoff = abs(xoff)

        if(orientation=='N'):
            straight_orient = 'V'
            w = H*(1 + 2*rat)
            l = H*rat
            straight = self.straight_trench(feedlength, x0 , y0-feedlength, straight_orient)
            feed = [self.rect(w,l, xstrt-xoff, y0-H-l)]        
        elif(orientation=='S'):
            straight_orient = 'V'
            w = H*(1 + 2*rat)
            l = H*rat
            straight = self.straight_trench(feedlength, x0, y0, straight_orient)
            feed = [self.rect(w,l, xstrt-xoff, y0+H)]
        elif(orientation=='E'):
            straight_orient = 'H'
            w = H*rat
            l = H*(1 + 2*rat)
            straight = self.straight_trench(feedlength, x0, y0-feedlength, straight_orient)
            feed = [self.rect(w,l, xstrt-xoff, y0_rect-300)]
        elif(orientation=='W'):
            straight_orient = 'H'
            w = H*rat
            l = H*(1 + 2*rat)
            straight = self.straight_trench(feedlength, x0, y0-feedlength, straight_orient)        
            feed = [self.rect(w,l, xstrt-xoff, y0_rect-300)]
        
        #feed = [self.rect(w,l, self.__xbound-H/2, y0_rect)]

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


    def make_feedbond_remove(self,feedlength,cc,rat,bond, x0, y0,xstr,ystr,xend,orientation):
        feedbond = self.feedbond_remove(feedlength,cc,rat,bond,x0, y0,xstr,ystr,xend, orientation)
        for i in feedbond:
            self.__cell.add(gdspy.Polygon(i, self.__layer+1))    
        return feedbond

class Quarterwave(Shapes):
    def __init__(self):
        self.__rs.__init__()
        return

class Halfwave(Shapes):
    def __init__(self):
        self.__rs.__init__()
        return
