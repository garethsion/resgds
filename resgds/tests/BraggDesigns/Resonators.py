#!/usr/bin/env python

"""
    This program contains the class which allows for defining the gds patterns
"""

import numpy as np
import gdspy

class ResonatorShapes(object):
	def __init__(self,cell):
        self.__cell = cell
        return

    def rect(self, w, l, x0, y0):
        '''
            List of tuples
            Recangle of width and length w and l with bottom left corner at (x0, y0).
        '''
        return [(x0, y0), (x0 + w, y0), (x0 + w, y0 + l), (x0, y0 + l)]

    def triangle(self,x0,y0,x1,y1,x2,y2,x3,y3):
        return[(x0,y0),(x1,y1),(x2,y2),(x3,y3)]

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

class ResonatorTrenches(ResonatorShapes):

	def __init__(self):
		ResonatorShapes.__init__(self)

    def halfarc_trench(self,r, width, gap, x0, y0, orient='E', npoints=40):
        """
        Defines a trench 180 degree 180 degree turn of conductor surrounded by two gap sections
        """
        inside = self.halfarc(r, gap, x0, y0, orientation=orient, npoints=npoints)
        outside = self.halfarc(r + gap + width, gap, x0, y0, orientation=orient, npoints=npoints)
        return [inside, outside]

    def quarterarc_trench(self,r, width, gap, x0, y0, orient='NE', npoints=20):
        """
        Defines a trench 90 degree 180 degree turn of conductor surrounded by two gap sections
        """
        inside = self.quarterarc(r, gap, x0, y0, orientation=orient, npoints=npoints)
        outside = self.quarterarc(r + gap + width, gap, x0, y0, orientation=orient, 
                npoints=npoints)
        return [inside, outside]

    def straight_trench(self, l, w, gap, x0, y0, orientation):
        """
        Defines a straight conductor surrounded by two gap sections
        """
        if orientation == 'H':
            return [self.rect(l, gap, x0, y0), self.rect(l, gap, x0, y0 + gap + w)]
        if orientation == 'V':
            return [self.rect(gap, l, x0, y0), self.rect(gap, l, x0 + gap + w, y0)]

class ResonatorStructures(ResonatorShapes, ResonatorStructures):
	def __init__(self):
		ResonatorShapes.__init__(self)
		ResonatorTrenches.__init__(self)

	def quarterwave(self,wqw,gqw,rqw,xq0,yq0,lo=50,feedline_sep=30):
		
		coords = lambda x,dx=0: x+dx

		xq1, yq1 = [coords(xq0,-gqw),coords(yq0,-feedline_sep)]
		qw = [rs.rect(gqw,wqw+2*gqw,xq1, yq1)]

		xq2, yq2 = [coords(xq0),coords(yq0,-feedline_sep)]
		qw += rs.straight_trench(ls,wqw,gqw, xq2, yq2, orientation='H')

		xq3, yq3 = [coords(xq2,ls),coords(yq2,-rqw)]
		qw += rs.halfarc_trench(rqw,wqw,gqw,xq3,yq3,orient='E',npoints=40)

		xq4, yq4 = [coords(xq3),coords(yq3,-rqw-wqw-2*gqw)]
		qw += rs.straight_trench(-ls,wqw,gqw, xq4, yq4, orientation='H')

		xq5, yq5 = [coords(xq4,-ls),coords(yq4,-rqw)]
		qw += rs.halfarc_trench(rqw,wqw,gqw,xq5,yq5,orient='W',npoints=40)

		xq6, yq6 = [coords(xq5),coords(yq5,-rqw-wqw-2*gqw)]
		qw += rs.straight_trench(ls,wqw,gqw, xq6, yq6, orientation='H')

		xq7, yq7 = [coords(xq6,ls),coords(yq6,-rqw)]
		qw += rs.halfarc_trench(rqw,wqw,gqw,xq7,yq7,orient='E',npoints=40)

		xq8, yq8 = [coords(xq7),coords(yq7,-rqw-wqw-2*gqw)]
		qw += rs.straight_trench(-ls,wqw,gqw, xq8, yq8, orientation='H')

		xq9, yq9 = [coords(xq8,-ls),coords(yq8,-rqw)]
		qw += rs.halfarc_trench(rqw,wqw,gqw,xq9,yq9,orient='W',npoints=40)

		xq10, yq10 = [coords(xq9),coords(yq9,-rqw-wqw-2*gqw)]
		qw += rs.straight_trench(ls,wqw,gqw, xq10, yq10, orientation='H')

		xq11, yq11 = [coords(xq10,ls),coords(yq10,-rqw)]
		qw += rs.halfarc_trench(rqw,wqw,gqw,xq11,yq11,orient='E',npoints=40)

		xq12, yq12 = [coords(xq11),coords(yq11,-rqw-wqw-2*gqw)]
		qw += rs.straight_trench(-ls,wqw,gqw, xq12, yq12, orientation='H')

		xq13, yq13 = [coords(xq12,-ls),coords(yq12,-rqw)]
		qw += rs.quarterarc_trench(rqw,wqw,gqw,xq13,yq13,orient='NW',npoints=40)

		xq14, yq14 = [coords(xq13,-rqw-2*gqw-wqw),coords(yq13)]
		qw += rs.straight_trench(-lo,wqw,gqw, xq14, yq14, orientation='V')

		return qw

	def quarterwave_remove(self,wqw,gqw,rqw,xq0,yq0,lo=50,feedline_sep=30):

		rm_width = wqw + 4*gqw
		arcrad = rqw - rm_width/2 + gqw + wqw/2

		xq2, yq2 = [coords(xq0,-2*gqw),
			coords(yq0,-feedline_sep + gqw + wqw/2 - rm_width/2)]
		qwr = [rs.rect(ls+2*gqw,rm_width, xq2, yq2)]

		xq3, yq3 = [coords(xq2,ls+2*gqw),coords(yq2,-arcrad)]
		qwr += [rs.halfarc(arcrad,rm_width,xq3,yq3,orientation='E',npoints=40)]

		xq4, yq4 = [coords(xq3),coords(yq3,-arcrad-rm_width)]
		qwr += [rs.rect(-ls,rm_width, xq4, yq4)]

		xq5, yq5 = [coords(xq4,-ls),coords(yq4,-arcrad)]
		qwr += [rs.halfarc(arcrad,rm_width,xq5,yq5,orientation='W',npoints=40)]

		xq6, yq6 = [coords(xq5),coords(yq5,-arcrad-rm_width)]
		qwr += [rs.rect(ls,rm_width, xq6, yq6)]

		xq7, yq7 = [coords(xq6,ls),coords(yq6,-arcrad)]
		qwr += [rs.halfarc(arcrad,rm_width,xq7,yq7,orientation='E',npoints=40)]

		xq8, yq8 = [coords(xq7),coords(yq7,-arcrad-rm_width)]
		qwr += [rs.rect(-ls,rm_width, xq8, yq8)]

		xq9, yq9 = [coords(xq8,-ls),coords(yq8,-arcrad)]
		qwr += [rs.halfarc(arcrad,rm_width,xq9,yq9,orientation='W',npoints=40)]

		xq10, yq10 = [coords(xq9),coords(yq9,-arcrad-rm_width)]
		qwr += [rs.rect(ls,rm_width, xq10, yq10)]

		xq11, yq11 = [coords(xq10,ls),coords(yq10,-arcrad)]
		qwr += [rs.halfarc(arcrad,rm_width,xq11,yq11,orientation='E',npoints=40)]

		xq12, yq12 = [coords(xq11),coords(yq11,-arcrad-rm_width)]
		qwr += [rs.rect(-ls,rm_width, xq12, yq12)]

		xq13, yq13 = [coords(xq12,-ls),coords(yq12,-arcrad)]
		qwr += [rs.quarterarc(arcrad,rm_width,xq13,yq13,orientation='NW',npoints=40)]

		xq14, yq14 = [coords(xq13,-arcrad-rm_width),coords(yq13)]
		qwr += [rs.rect(rm_width,-lo, xq14, yq14)]

		return qwr

	def feedline(self,x0,y0,wfeed,gfeed,feedwidth=3000,lbond=300,lfeed1=600):

		x1,y1 = [coords(x0),coords(y0,-lbond)]
		feed = rs.straight_trench(lfeed1,wfeed,gfeed, x1, y1, orientation='V')

		x2,y2 = [coords(x1,rfeed+wtot),coords(y1,lfeed1)]
		feed += rs.quarterarc_trench(rfeed,wfeed,gfeed,x2,y2,orient='NW',npoints=40)

		x3,y3 = [coords(x0,feedwidth),coords(y0,-lbond)]
		feed += rs.straight_trench(lfeed1,wfeed,gfeed, x3, y3, orientation='V')

		x4,y4 = [coords(x3,-rfeed),coords(y3,lfeed1)]
		feed += rs.quarterarc_trench(rfeed,wfeed,gfeed,x4,y4,orient='NE',npoints=40)

		lfeed2 = feedwidth - (x2-x0) - (x3-x4) #- 2*(x2-x0)
		x5,y5 = [coords(x2),coords(y2,rfeed)]
		feed += rs.straight_trench(lfeed2,wfeed,gfeed, x5, y5, orientation='H')

		feed_coords = [x5,y5,lfeed2]

		return feed,feed_coords

	def feedline_remove(x0,y0,wfeed,gfeed,rfeed,feedwidth=3000,lbond=300,lfeed1=600):

		rm_width = 4*wfeed + 2*gfeed
		arcrad = .5*(2*rfeed - 4*gfeed - wfeed)

		x1,y1 = [coords(x0,(wfeed/2)+gfeed-rm_width/2),coords(y0,-lbond)]
		feedr = [rs.rect(rm_width,lfeed1, x1, y1)]

		x2,y2 = [coords(x1,arcrad+rm_width),coords(y1,lfeed1)]
		feedr += [rs.quarterarc(arcrad,rm_width,x2,y2,orientation='NW',npoints=40)]

		x3,y3 = [coords(x1,feedwidth),coords(y0,-lbond)]
		feedr += [rs.rect(rm_width,lfeed1, x3, y3)]

		x4,y4 = [coords(x3,-arcrad),coords(y3,lfeed1)]
		feedr += [rs.quarterarc(arcrad,rm_width,x4,y4,orientation='NE',npoints=40)]

		lfeed2 = feedwidth - (x2-x1) - (x3-x4) 
		x5,y5 = [coords(x2),coords(y2,arcrad)]
		feedr += [rs.rect(lfeed2,rm_width, x5, y5)]

		return feedr

		def feedbond(x0,y0,w,g,feedlength=300,bondlength=600,bondl=150):

		bondw = 4*bondl

		xbond = x0 - bondw/2 + gfeed + wfeed/2
		ybond = y0 - feedlength - bondl - bondlength

		x0b = x0
		y0b = y0 - feedlength

		x0b2 = x0b + gfeed + wfeed

		x1 = xbond
		y1 = ybond + bondl

		x2 = xbond + bondw - bondl
		y2 = ybond + bondl + feedlength

		feed = [rs.rect(bondw,bondl, xbond, ybond)]
		feed += [rs.rect(bondl,feedlength,xbond,ybond+bondl)]
		feed += [rs.rect(bondl,feedlength,xbond+bondw-bondl,ybond+bondl)]

		d1 = [(x0b, y0b), (x0b+gfeed, y0b), (x1+bondl, y2), (x1, y2)]
		d2 = [(x0b2, y0b), (x0b2+gfeed, y0b), (x1+bondw, y2), (x1+bondw-bondl, y2)]
		feed += [d1,d2]

		return feed

	def feedbond_remove(x0,y0,w,g,feedlength=300,bondlength=750,bondl=150):

		rm_width = 4*w + 2*g
		bondw = 4*bondl
		bondwr = 6*bondl
		bondlr = bondl

		xbond = x0 - bondwr/2 + gfeed + wfeed/2
		ybond = y0 - feedlength - bondl - bondlength

		x0b = x0
		y0b = y0 - feedlength

		x0b2 = x0b + gfeed + wfeed

		x1 = xbond
		y1 = ybond + bondl

		x2 = xbond + bondwr - bondlr
		y2 = ybond + bondlr + feedlength

		fbondr = [rs.rect(bondwr,bondwr-2*bondlr, xbond, ybond)]

		trix0 = (x0b + g + w/2) - rm_width/2
		triy1 = ybond - bondlr+bondl+bondw

		d1 = [(trix0, y0b), (trix0+rm_width, y0b), (x1+bondwr, triy1), (x1, triy1)]
		fbondr += [d1]

		return fbondr 


class BuildShapes:
	def __init__(self,cell):
		self.__cell = cell

	def boolean(self,input_shape,bool_shape, input_layer=0, output_layer=0,mode='or'):

		if(mode != 'or' or mode != 'not' or mode != 'and'):
			raise Exception('mode should be either 'not', 'or', or 'and'')

		for i in range(0,len(input_shape)):
			shape = gdspy.Polygon(input_shape[i],input_layer)
			output_bool = gdspy.fast_boolean(bool_shape,shape, mode, 
				precision=1e-9, max_points=1000, layer=output_layer)
		return shape, output_bool

	def build(self,shape,cell):
		return self.__cell.add(shape)


