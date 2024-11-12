#!/usr/bin/env python
import os
from resgds import *
from resgds.interface import *
import gdspy # gds library
import numpy as np
from resgds.resonatorshapes import Shapes

class ResTempFiles:

	def __init__(self,cell):
		self.__rs = Shapes(cell)
		self.coords = lambda x,dx=0: x+dx

	def lengths(self,w,g,r,l,lin=100,lout=100,no_arcs=4):

		arclength = self.arclength(w,g,r)

		tot_arc_length = no_arcs * arclength
		tot_arc_length += arclength

		lremain = l - tot_arc_length - lin - lout 
		lremain += arclength

		lstrait = lremain / no_arcs

		ls = [lin]
		# l.append(arclength)
		ls.append((lstrait/2)-arclength/2)
		ls.append(lstrait)
		ls.append(lout)

		# arc = [arclength]
		# arc.append(arclength/2)

		# print(3*lstrait + 4*arclength + arclength + lin + lout + 2*(lstrait/2 - arclength/2))

		return ls, arclength

	def arclength(self,w,g,r):
		out_LHS = g
		out_RHS = 2*w + 3*g + 2*r 
			
		diameter = out_RHS - out_LHS - (w/2)
		
		arclength = .5 * diameter * np.pi
		arctot = 2*arclength
		
		return arctot

	# def feedbond(x0,y0,w,g,feedlength=300,bondlength=600,bondh=150):

	# 	bondw = 4*bondh

	# 	xbond = x0 - bondw/2 + gfeed + wfeed/2
	# 	ybond = y0 - feedlength - bondh - bondlength

	# 	x0b = x0
	# 	y0b = y0 - feedlength

	# 	x0b2 = x0b + gfeed + wfeed

	# 	x1 = xbond
	# 	y1 = ybond + bondh

	# 	x2 = xbond + bondw - bondh
	# 	y2 = ybond + bondh + feedlength

	# 	feed = [rs.rect(bondw,bondh, xbond, ybond)]
	# 	feed += [rs.rect(bondh,feedlength,xbond,ybond+bondh)]
	# 	feed += [rs.rect(bondh,feedlength,xbond+bondw-bondh,ybond+bondh)]

	# 	d1 = [(x0b, y0b), (x0b+gfeed, y0b), (x1+bondh, y2), (x1, y2)]
	# 	d2 = [(x0b2, y0b), (x0b2+gfeed, y0b), (x1+bondw, y2), (x1+bondw-bondh, y2)]
	# 	feed += [d1,d2]

	# 	return feed

	def feedbond(self,x0,y0,w,g,feedlength=300,bondlength=600,bondh=150,orientation='N'):

		if(orientation == 'N'):
			bondw = 4*bondh

			xbond = x0 - .5*bondw + g 
			ybond = y0 + bondw - bondh 
			#- bondh + bondw + .5*w + g


			feed = [self.__rs.rect(bondw,bondh, xbond, ybond)]
			feed += [self.__rs.rect(bondh, feedlength,xbond,ybond-2*bondh)]
			feed += [self.__rs.rect(bondh, feedlength,xbond+bondw-bondh,ybond-2*bondh)]

			xa = xbond
			ya = ybond-2*bondh

			xb = xa+feedlength
			# yb = ya-bondw/2-g-w/2
			yb = ya - bondh

			d1 = [(xa, ya), (xa+bondh, ya), (xb, yb), (xb-g, yb)]
			d2 = [(xa+bondw-bondh,ya), (xa+bondw, ya), (xb+w+g, yb), (xb+w, yb)]
			feed += [d1,d2]

		if(orientation == 'E'):
			bondw = 4*bondh

			xbond = x0 - bondlength - bondh#- bondw/2 + gfeed + wfeed/2
			ybond = y0 - bondw/2 + g + w/2# - feedlength - bondh - bondlength

			feed = [self.__rs.rect(bondh,bondw, xbond, ybond)]
			feed += [self.__rs.rect(feedlength,bondh,xbond+bondh,ybond)]
			feed += [self.__rs.rect(feedlength,bondh,xbond+bondh,ybond+bondw-bondh)]

			xa = xbond+bondw-bondh
			ya = ybond+bondw

			xb = xa+feedlength
			yb = ya-bondw/2-g-w/2

			d1 = [(xa, ya), (xa, ya-bondh), (xb, yb+g+w), (xb, yb+2*g+w)]
			d2 = [(xa, ya-bondw), (xa, ya-bondw+bondh), (xb, yb+g), (xb, yb)]
			feed += [d1,d2]

		if(orientation == 'S'):
			bondw = 4*bondh

			xbond = x0 - .5*bondw + g 
			ybond = y0 - bondh - bondw - .5*w - g


			feed = [self.__rs.rect(bondw,bondh, xbond, ybond)]
			feed += [self.__rs.rect(bondh, feedlength,xbond,ybond+bondh)]
			feed += [self.__rs.rect(bondh, feedlength,xbond+bondw-bondh,ybond+bondh)]

			xa = xbond
			ya = ybond+bondw-bondh

			xb = xa+feedlength
			yb = ya+bondw/2+g+w/2

			d1 = [(xa, ya), (xa+bondh, ya), (xb, yb), (xb-g, yb)]
			d2 = [(xa+bondw-bondh,ya), (xa+bondw, ya), (xb+w+g, yb), (xb+w, yb)]
			feed += [d1,d2]

		if(orientation == 'W'):
			bondw = 4*bondh

			# y0 = y0 + bondw

			xbond = x0  + bondlength#+ bondlength#+ bondlength + bondh 
			ybond = y0 - bondw/2 + g + w/2
			# xbond = x0 + bondw/2 + gfeed + wfeed/2 + feedlength
			# ybond = y0 - feedlength - bondh - bondlength


			feed = [self.__rs.rect(bondh,bondw, xbond, ybond)]
			feed += [self.__rs.rect(feedlength,bondh,xbond-2*bondh,ybond)]
			feed += [self.__rs.rect(feedlength,bondh,xbond-2*bondh,ybond+bondw-bondh)]

			xa = xbond-2*bondh
			ya = ybond+bondw

			xb = xa-feedlength
			yb = ya-bondw/2-g-w/2

			d1 = [(xa, ya), (xa, ya-bondh), (xb, yb+g+w), (xb, yb+2*g+w)]
			d2 = [(xa, ya-bondw), (xa, ya-bondw+bondh), (xb, yb+g), (xb, yb)]
			feed += [d1,d2]

		return feed

	def feedbond_remove(self,x0,y0,w,g,feedlength=300,bondlength=750,bondh=150,orientation='E'):

		# rm_width = 4*w + 2*g
		# bondw = 4*bondh
		# bondwr = 6*bondh
		# bondhr = bondh

		# xbond = x0 - bondwr/2 + g + w/2
		# ybond = y0 - feedlength - bondh - bondlength

		# x0b = x0
		# y0b = y0 - feedlength

		# x0b2 = x0b + g + w

		# x1 = xbond
		# y1 = ybond + bondh

		# x2 = xbond + bondwr - bondhr
		# y2 = ybond + bondhr + feedlength

		# fbondr = [self.__rs.rect(bondwr,bondwr-2*bondhr, xbond, ybond)]

		# trix0 = (x0b + g + w/2) - rm_width/2
		# triy1 = ybond - bondhr+bondh+bondw

		# d1 = [(trix0, y0b), (trix0+rm_width, y0b), (x1+bondwr, triy1), (x1, triy1)]
		# fbondr += [d1]

		rm_width = 4*w + 2*g
		bondw = 4*bondh
		bondwr = 5*bondh
		bondhr = bondh

		if(orientation == 'N'):

			xbond = x0 - bondlength - bondh - rm_width#- bondw/2 + gfeed + wfeed/2
			ybond = y0 - bondwr/2 + g + w/2# - feedlength - bondh - bondlength

			sqw = rm_width + bondw -bondh
			fbondr = [self.__rs.rect(bondwr, sqw, xbond, ybond)]
			
			xa = xbond + bondwr
			ya = ybond + 2*sqw 
			ybond = ybond + sqw
			# xa = xbond + bondwr
			
			yb = ya - bondwr/2
			triy = rm_width/2

			# d1 = [(xa,ya), (xa, ybond), (xa+2*bondhr,yb-triy),(xa+2*bondhr,yb+triy) ]
			# d1 = [(xa,xa), (xa,xbond), (xa+2*bondhr,yb-triy), (xa+2*bondhr,yb+triy)]
			# d1 = [(xa, ya), (xbond+.5*bondwr+rm_width,ybond), (xbond+.5*bondwr-rm_width,ybond), (xbond,ya)]
			d1 = [(xa, ybond), (xbond+.5*bondwr+rm_width,ya), (xbond+.5*bondwr-rm_width,ya), (xbond,ybond)]
			fbondr += [d1]

		if(orientation == 'E'):

			xbond = x0 - bondlength - bondh - rm_width#- bondw/2 + gfeed + wfeed/2
			ybond = y0 - bondwr/2 + g + w/2# - feedlength - bondh - bondlength

			sqw = rm_width + bondw -bondh
			fbondr = [self.__rs.rect(sqw,bondwr, xbond, ybond)]
			
			xa = xbond + sqw
			ya = ybond + bondwr

			yb = ya - bondwr/2
			triy = rm_width/2

			d1 = [(xa,ya), (xa, ybond), (xa+2*bondhr,yb-triy),(xa+2*bondhr,yb+triy) ]
			fbondr += [d1]

		if(orientation == 'S'):

			xbond = x0 - bondlength - bondh - rm_width#- bondw/2 + gfeed + wfeed/2
			ybond = y0 - bondwr + g + w/2# - feedlength - bondh - bondlength

			sqw = rm_width + bondw -bondh
			fbondr = [self.__rs.rect(bondwr, sqw, xbond, y0+.5*bondlength-.5*rm_width)]
			
			xa = xbond + bondwr
			ya = ybond + sqw 
			ybond = ybond + 2*sqw
			# xa = xbond + bondwr
			
			yb = ya - bondwr/2
			triy = rm_width/2

			# d1 = [(xa,ya), (xa, ybond), (xa+2*bondhr,yb-triy),(xa+2*bondhr,yb+triy) ]
			# d1 = [(xa,xa), (xa,xbond), (xa+2*bondhr,yb-triy), (xa+2*bondhr,yb+triy)]
			# d1 = [(xa, ya), (xbond+.5*bondwr+rm_width,ybond), (xbond+.5*bondwr-rm_width,ybond), (xbond,ya)]
			d1 = [(xa, ybond), (xbond+.5*bondwr+rm_width,ya), (xbond+.5*bondwr-rm_width,ya), (xbond,ybond)]
			fbondr += [d1]

		if(orientation == 'W'):

			xbond = x0 + 2*bondh#+ bondlength  - rm_width
			ybond = y0 - bondwr/2 + g + w/2

			sqw = rm_width + bondw -bondh
			fbondr = [self.__rs.rect(sqw,bondwr, xbond, ybond)]
			
			xa = xbond-2*bondhr
			ya = ybond + bondwr

			yb = ya - bondwr/2
			triy = rm_width/2

			d1 = [(xbond,ya), (xbond, ybond), (xa,yb-triy),(xa,yb+triy) ]
			fbondr += [d1]

		return fbondr 

	def quarterwave(wqw,gqw,rqw,xq0,yq0,lo=50,feedline_sep=30):

		xq1, yq1 = [self.coords(xq0,-gqw),self.coords(yq0,-feedline_sep)]
		qw = [self.__rs.rect(gqw,wqw+2*gqw,xq1, yq1)]

		xq2, yq2 = [self.coords(xq0),self.coords(yq0,-feedline_sep)]
		qw += self.__rs.straight_trench(ls,wqw,gqw, xq2, yq2, orientation='H')

		xq3, yq3 = [self.coords(xq2,ls),self.coords(yq2,-rqw)]
		qw += self.__rs.halfarc_trench(rqw,wqw,gqw,xq3,yq3,orient='E',npoints=40)

		xq4, yq4 = [self.coords(xq3),self.coords(yq3,-rqw-wqw-2*gqw)]
		qw += self.__rs.straight_trench(-ls,wqw,gqw, xq4, yq4, orientation='H')

		xq5, yq5 = [self.coords(xq4,-ls),self.coords(yq4,-rqw)]
		qw += self.vrs.halfarc_trench(rqw,wqw,gqw,xq5,yq5,orient='W',npoints=40)

		xq6, yq6 = [self.coords(xq5),self.coords(yq5,-rqw-wqw-2*gqw)]
		qw += self.__rs.straight_trench(ls,wqw,gqw, xq6, yq6, orientation='H')

		xq7, yq7 = [self.coords(xq6,ls),self.coords(yq6,-rqw)]
		qw += self.__rs.halfarc_trench(rqw,wqw,gqw,xq7,yq7,orient='E',npoints=40)

		xq8, yq8 = [self.coords(xq7),self.coords(yq7,-rqw-wqw-2*gqw)]
		qw += self.__rs.straight_trench(-ls,wqw,gqw, xq8, yq8, orientation='H')

		xq9, yq9 = [self.coords(xq8,-ls),self.coords(yq8,-rqw)]
		qw += self.__rs.halfarc_trench(rqw,wqw,gqw,xq9,yq9,orient='W',npoints=40)

		xq10, yq10 = [self.coords(xq9),self.coords(yq9,-rqw-wqw-2*gqw)]
		qw += self.__rs.straight_trench(ls,wqw,gqw, xq10, yq10, orientation='H')

		xq11, yq11 = [self.coords(xq10,ls),self.coords(yq10,-rqw)]
		qw += self.__rs.halfarc_trench(rqw,wqw,gqw,xq11,yq11,orient='E',npoints=40)

		xq12, yq12 = [self.coords(xq11),self.coords(yq11,-rqw-wqw-2*gqw)]
		qw += self.__rs.straight_trench(-ls,wqw,gqw, xq12, yq12, orientation='H')

		xq13, yq13 = [self.coords(xq12,-ls),self.coords(yq12,-rqw)]
		qw += self.__rs.quarterarc_trench(rqw,wqw,gqw,xq13,yq13,orient='NW',npoints=40)

		xq14, yq14 = [self.coords(xq13,-rqw-2*gqw-wqw),self.coords(yq13)]
		qw += self.__rs.straight_trench(-lo,wqw,gqw, xq14, yq14, orientation='V')

		return qw

	def quarterwave_remove(self,wqw,gqw,rqw,xq0,yq0,lo=50,feedline_sep=30):

		rm_width = wqw + 4*gqw
		arcrad = rqw - rm_width/2 + gqw + wqw/2

		xq2, yq2 = [self.coords(xq0,-2*gqw),
			self.coords(yq0,-feedline_sep + gqw + wqw/2 - rm_width/2)]
		qwr = [self.__rs.rect(ls+2*gqw,rm_width, xq2, yq2)]

		xq3, yq3 = [self.coords(xq2,ls+2*gqw),self.coords(yq2,-arcrad)]
		qwr += [self.__rs.halfarc(arcrad,rm_width,xq3,yq3,orientation='E',npoints=40)]

		xq4, yq4 = [self.coords(xq3),self.coords(yq3,-arcrad-rm_width)]
		qwr += [self.__rs.rect(-ls,rm_width, xq4, yq4)]

		xq5, yq5 = [self.coords(xq4,-ls),self.coords(yq4,-arcrad)]
		qwr += [self.__rs.halfarc(arcrad,rm_width,xq5,yq5,orientation='W',npoints=40)]

		xq6, yq6 = [self.coords(xq5),self.coords(yq5,-arcrad-rm_width)]
		qwr += [self.__rs.rect(ls,rm_width, xq6, yq6)]

		xq7, yq7 = [self.coords(xq6,ls),self.coords(yq6,-arcrad)]
		qwr += [self.__rs.halfarc(arcrad,rm_width,xq7,yq7,orientation='E',npoints=40)]

		xq8, yq8 = [self.coords(xq7),self.coords(yq7,-arcrad-rm_width)]
		qwr += [self.__rs.rect(-ls,rm_width, xq8, yq8)]

		xq9, yq9 = [self.coords(xq8,-ls),self.coords(yq8,-arcrad)]
		qwr += [self.__rs.halfarc(arcrad,rm_width,xq9,yq9,orientation='W',npoints=40)]

		xq10, yq10 = [self.coords(xq9),self.coords(yq9,-arcrad-rm_width)]
		qwr += [self.__rs.rect(ls,rm_width, xq10, yq10)]

		xq11, yq11 = [self.coords(xq10,ls),self.coords(yq10,-arcrad)]
		qwr += [self.__rs.halfarc(arcrad,rm_width,xq11,yq11,orientation='E',npoints=40)]

		xq12, yq12 = [self.coords(xq11),self.coords(yq11,-arcrad-rm_width)]
		qwr += [self.__rs.rect(-ls,rm_width, xq12, yq12)]

		xq13, yq13 = [self.coords(xq12,-ls),self.coords(yq12,-arcrad)]
		qwr += [self.__rs.quarterarc(arcrad,rm_width,xq13,yq13,orientation='NW',npoints=40)]

		xq14, yq14 = [self.coords(xq13,-arcrad-rm_width),self.coords(yq13)]
		qwr += [self.__rs.rect(rm_width,-lo, xq14, yq14)]

		return qwr

	def halfwaveresonator(self,x1,y1,w,g,r,rfeed,arc,lcap,l1,l2,l3):

		wtot = w + 2*g
		x2, y2 = [ self.coords(x1,lcap), self.coords(y1) ]
		resonator = self.__rs.straight_trench(l1, w, g, x1, y1, orientation='H')

		x3, y3 = [ self.coords(x2,l1-lcap), self.coords(y1,rfeed+wtot) ]
		resonator += self.__rs.quarterarc_trench(rfeed, w, g, x3, y3, orient='SE')

		x4, y4 = [ self.coords(x3,rfeed), self.coords(y3) ]
		resonator += self.__rs.straight_trench(l2+arc/2, w, g, x4, y4, orientation='V')

		x5, y5 = [ self.coords(x4,rfeed+wtot), self.coords(y4,l2+arc/2) ]
		resonator += self.__rs.halfarc_trench(rfeed, w, g, x5, y5, orient='N')

		x6, y6 = [ self.coords(x5,rfeed), self.coords(y5) ]
		resonator += self.__rs.straight_trench(-l3, w, g, x6, y6, orientation='V')

		x7, y7 = [ self.coords(x6,rfeed+wtot), self.coords(y6,-l3) ]
		resonator += self.__rs.halfarc_trench(rfeed, w, g, x7, y7, orient='S')

		x8, y8 = [ self.coords(x7,rfeed), self.coords(y7) ]
		resonator += self.__rs.straight_trench(l3, w, g, x8, y8, orientation='V')

		x9, y9 = [ self.coords(x8,rfeed+wtot), self.coords(y8,l3) ]
		resonator += self.__rs.halfarc_trench(rfeed, w, g, x9, y9, orient='N')

		x10, y10 = [ self.coords(x9,rfeed), self.coords(y9) ]
		resonator += self.__rs.straight_trench(-l3, w, g, x10, y10, orientation='V')

		x11, y11 = [ self.coords(x10,rfeed+wtot), self.coords(y10,-l3) ]
		resonator += self.__rs.halfarc_trench(rfeed, w, g, x11, y11, orient='S')

		x12, y12 = [ self.coords(x11,rfeed), self.coords(y11) ]
		resonator += self.__rs.straight_trench(l2, w, g, x12, y12, orientation='V')

		x13, y13 = [ self.coords(x12,rfeed+wtot), self.coords(y12,l2) ]
		resonator += self.__rs.quarterarc_trench(rfeed, w, g, x13, y13, orient='NW')

		x14, y14 = [ self.coords(x13), self.coords(y13,rfeed) ]
		resonator += self.__rs.straight_trench(l1, w, g, x14, y14, orientation='H')

		return resonator

	def feedline(x0,y0,wfeed,gfeed,feedwidth=3000,lbond=300,lfeed1=600):

		x1,y1 = [self.coords(x0),self.coords(y0,-lbond)]
		feed = rs.straight_trench(lfeed1,wfeed,gfeed, x1, y1, orientation='V')

		x2,y2 = [self.coords(x1,rfeed+wtot),self.coords(y1,lfeed1)]
		feed += rs.quarterarc_trench(rfeed,wfeed,gfeed,x2,y2,orient='NW',npoints=40)

		x3,y3 = [self.coords(x0,feedwidth),self.coords(y0,-lbond)]
		feed += rs.straight_trench(lfeed1,wfeed,gfeed, x3, y3, orientation='V')

		x4,y4 = [self.coords(x3,-rfeed),self.coords(y3,lfeed1)]
		feed += rs.quarterarc_trench(rfeed,wfeed,gfeed,x4,y4,orient='NE',npoints=40)

		lfeed2 = feedwidth - (x2-x0) - (x3-x4) #- 2*(x2-x0)
		x5,y5 = [self.coords(x2),self.coords(y2,rfeed)]
		feed += rs.straight_trench(lfeed2,wfeed,gfeed, x5, y5, orientation='H')

		feed_self.coords = [x5,y5,lfeed2]

		return feed,feed_self.coords

	def feedline_remove(x0,y0,wfeed,gfeed,rfeed,feedwidth=3000,lbond=300,lfeed1=600):

		rm_width = 4*wfeed + 2*gfeed
		arcrad = .5*(2*rfeed - 4*gfeed - wfeed)

		x1,y1 = [self.coords(x0,(wfeed/2)+gfeed-rm_width/2),self.coords(y0,-lbond)]
		feedr = [rs.rect(rm_width,lfeed1, x1, y1)]

		x2,y2 = [self.coords(x1,arcrad+rm_width),self.coords(y1,lfeed1)]
		feedr += [rs.quarterarc(arcrad,rm_width,x2,y2,orientation='NW',npoints=40)]

		x3,y3 = [self.coords(x1,feedwidth),self.coords(y0,-lbond)]
		feedr += [rs.rect(rm_width,lfeed1, x3, y3)]

		x4,y4 = [self.coords(x3,-arcrad),self.coords(y3,lfeed1)]
		feedr += [rs.quarterarc(arcrad,rm_width,x4,y4,orientation='NE',npoints=40)]

		lfeed2 = feedwidth - (x2-x1) - (x3-x4) 
		x5,y5 = [self.coords(x2),self.coords(y2,arcrad)]
		feedr += [rs.rect(lfeed2,rm_width, x5, y5)]

		return feedr

	def boolean(self,input_shape,bool_shape, input_layer=0, output_layer=0,mode='or'):

		# if(mode != str('or') or mode != str('not') or mode != str('and')):
		# 	raise Exception('mode should be either \'not\', \'or\', or \'and\'')

		for i in range(0,len(input_shape)):
			shape = gdspy.Polygon(input_shape[i],input_layer)
			bool_shape = gdspy.fast_boolean(bool_shape,shape,mode, 
				precision=1e-9, max_points=1000, layer=output_layer)

		return bool_shape

	def build(self,input_shape,cell,input_layer=0):

		# if(mode != str('or') or mode != str('not') or mode != str('and')):
		# 	raise Exception('mode should be either \'not\', \'or\', or \'and\'')

		for i in range(0,len(input_shape)):
			shape = gdspy.Polygon(input_shape[i],input_layer)
			cell.add(shape)
		return shape

	def build2(self,shape,cell):
		return cell.add(shape)
		for i in range(0,len(input_shape)):
			shape = gdspy.Polygon(input_shape[i],input_layer)
			output_bool = gdspy.fast_boolean(bool_shape,shape, mode, 
				precision=1e-9, max_points=1000, layer=output_layer)
		return shape, output_bool
