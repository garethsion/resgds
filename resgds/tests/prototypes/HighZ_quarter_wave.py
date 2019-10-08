#!/usr/bin/env python
import os
from resgds import *
from interface import Interface
import gdspy # gds library
import numpy as np

# Layout filename
layout_file ='HighZ_quarter_wave.gds'

def lengths(w,g,r,l):
    out_LHS = g
    out_RHS = 2*w + 3*g + 2*r 
        
    diameter = out_RHS - out_LHS - (w/2)
    
    arclength = .5 * diameter * np.pi
    arctot = 2*arclength
    len_remain = l - arctot

    l1 = len_remain/6
    l2 = 3*l1
    l3 = 2*l1
    return l1, l2, l3, arclength

def arclength(w,g,r):
    out_LHS = g
    out_RHS = 2*w + 3*g + 2*r 
        
    diameter = out_RHS - out_LHS - (w/2)
    
    arclength = .5 * diameter * np.pi
    arctot = 2*arclength
    
    return arctot

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

def quarterwave(wqw,gqw,rqw,xq0,yq0,lo=50,feedline_sep=30):

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

def quarterwave_remove(wqw,gqw,rqw,xq0,yq0,lo=50,feedline_sep=30):

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

def feedline(x0,y0,wfeed,gfeed,feedwidth=3000,lbond=300,lfeed1=600):

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

# Parameters
###################################################################
sub_x, sub_y = [5000, 5000] # substrate dimensions
coords = lambda x,dx=0: x+dx
x0,y0 = [1000,2250]

wfeed, gfeed, lfeed = [35,21,5000] # Cavity width, gap, length
# wqw, gqw, lqw = [30.44,6.685,4051.32]  # Low Z section
wqw, gqw, lqw = [2,20.905,4051.32] # High Z section
wtot = 2*gfeed+wfeed

rfeed = 400

sub_layer = 0
dot_layer = 1
cond_layer = 2
remove_layer = 3

conductor = []
removes = []

# Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# SUBSTRATE
#########################################################################
sub = [rs.rect(sub_x,sub_y,0,0)]

for i in range(0,len(sub)):
	sub = gdspy.Polygon(sub[i],sub_layer)

# ANTI-DOTS
#########################################################################
layout = LayoutComponents(poly_cell, sub_x, sub_y,layer=dot_layer)
dots = layout.antidot_array(0,0,10,30,0)

# FEEDLINE
#########################################################################
feedwidth = 3000
lbond = 300
lfeed1 = 600

bondpad = feedbond(x0,y0,wfeed,gfeed,feedlength=lbond,bondlength=600,bondl=150)
bondpad += feedbond(x0+feedwidth,y0,wfeed,gfeed,feedlength=lbond,bondlength=600,bondl=150)

for i in range(0,len(bondpad)):
	inbond = gdspy.Polygon(bondpad[i],cond_layer)
	conductor = gdspy.fast_boolean(conductor,inbond, 'or', 
		precision=1e-9, max_points=1000, layer=cond_layer)

feed,feed_coords = feedline(x0,y0,wfeed,gfeed,feedwidth=3000,lbond=300,lfeed1=600)
x5,y5,lfeed2 = [ feed_coords[0], feed_coords[1], feed_coords[2] ]
for i in range(0,len(feed)):
	feedline = gdspy.Polygon(feed[i],cond_layer)
	conductor = gdspy.fast_boolean(conductor,feed, 'or', 
		precision=1e-9, max_points=1000, layer=cond_layer)

# FEEDLINE REMOVES
# ########################################################################
feedwidth = 3000
lbondr = 300
lfeed1 = 750

bondpad_remove = feedbond_remove(x0,y0,wfeed,gfeed,feedlength=lbond,bondlength=lfeed1,bondl=150)
bondpad_remove += feedbond_remove(x0+feedwidth,y0,wfeed,gfeed,feedlength=lbond,bondlength=lfeed1,bondl=150)

for i in range(0,len(bondpad_remove)):
	rem = gdspy.Polygon(bondpad_remove[i],remove_layer)
	dots = gdspy.fast_boolean(dots,rem,'not', 
		precision=1e-9, max_points=1000, layer=dot_layer)

feedr = feedline_remove(x0,y0,wfeed,gfeed,rfeed,feedwidth=3000,lbond=300,lfeed1=600)

for i in range(0,len(feedr)):
	rem = gdspy.Polygon(feedr[i],remove_layer)
	dots = gdspy.fast_boolean(dots,rem,'not', 
		precision=1e-9, max_points=1000, layer=dot_layer)

#QUARTERWAVE RESONATOR
#########################################################################
rqw = 30
larc = arclength(wqw,gqw,rqw)
lo = 50
ls = ( lqw - (5*larc) - (larc/2) - lo ) / 6

xq0, yq0 = [coords(x5,(lfeed2/2)-(ls/2)),coords(y5,-wqw-2*gqw)]
qw = quarterwave(wqw,gqw,rqw,xq0,yq0,lo=50,feedline_sep=30)

for i in range(0,len(qw)):
	resonator = gdspy.Polygon(qw[i],cond_layer)
	conductor = gdspy.fast_boolean(conductor,resonator, 'or', 
		precision=1e-9, max_points=1000, layer=cond_layer)

qwr = quarterwave_remove(wqw,gqw,rqw,xq0,yq0,lo=50,feedline_sep=30)

for i in range(0,len(qwr)):
	rem = gdspy.Polygon(qwr[i],remove_layer)
	dots = gdspy.fast_boolean(dots,rem,'not', 
		precision=1e-9, max_points=1000, layer=dot_layer)

# MAKE GDS LAYERS
##########################################################################
circuit = gdspy.fast_boolean(dots,conductor,'or',
	precision=1e-9, max_points=1000, layer=sub_layer)
poly_cell.add(circuit)

###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)