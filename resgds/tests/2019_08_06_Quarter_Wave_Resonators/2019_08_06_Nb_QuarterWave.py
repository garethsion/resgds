#!/usr/bin/env python

""" 
This modification of the Bragg resonator generator has a smaller footprint. 
This is to make the fabrication process easier, since I have had problems with
fitting the device onto the 10x5 chips
"""

import os
from resgds import *
import bragg
from interface import Interface
import gdspy # gds library
import numpy as np
from restempfiles import *


# Layout filename
layout_file ='fab_files/2019_08_06_Nb_QuarterWave.gds'

# Parameters
#__________________________________________________________
sub_x, sub_y = [4500, 4500] # substrate dimensions


# Start making resonator geometry
############################################################################

# Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)
rt = ResTempFiles(poly_cell)

# Substrate [layer 0]
sub = BuildRect(poly_cell, sub_x, sub_y, layer=0)
sub.make(0,0)

# Antidot array [layer 1]
layout = LayoutComponents(poly_cell, sub_x, sub_y,layer=1)
# layout.make_antidot_array(0,0,10,30,0)

# Feedline sections
# INPUT FEEDLINE
###############################################################################
wfeed = 30
gfeed = 20
rfeed = 250
coords = lambda x,dx=0: x+dx

# CREATE FEEDLINE SECTION
#########################
def section_lengths(w,g,r,l):

        out_LHS = g
        out_RHS = 2*w + 3*g + 2*r
        
        diameter = out_RHS - out_LHS - (w/2)
        
        arclength = .5 * diameter * np.pi
        arctot = 3*arclength
        len_remain = l - arctot

        l1= len_remain/4
        l2 = 1*l1
        l3 = 1*l1
        l4 = 1*l1

        return l1, l2, l3, l4, arclength

def full_feedline(wfeed,gfeed,x0,y0,inlength=800,feedwidth=3200,feedlength=300,bondlength=600,bondh=150):

	feed = rt.feedbond(x0,y0,wfeed,gfeed,feedlength=feedlength,bondlength=bondlength,bondh=bondh,orientation='N')

	x1,y1 = [coords(x0+feedlength-wfeed-2*gfeed),coords(y0,bondh+2*feedlength)]
	feed += rs.straight_trench(inlength,wfeed,gfeed,x1,y1,orientation='V')

	x2,y2 = [coords(x1, rfeed+2*gfeed+wfeed),coords(y1,inlength)]
	feed += rs.quarterarc_trench(rfeed,wfeed,gfeed,x2,y2,orient='NW')

	x3,y3 = [coords(x2),coords(y2,rfeed)]
	feed += rs.straight_trench(feedwidth,wfeed,gfeed,x3,y3,orientation='H')

	x4,y4 = [coords(x3, feedwidth),coords(y3,-rfeed)]
	feed += rs.quarterarc_trench(rfeed,wfeed,gfeed,x4,y4,orient='NE')

	x5,y5 = [coords(x4,rfeed),coords(y4)]
	feed += rs.straight_trench(-inlength,wfeed,gfeed,x5,y5,orientation='V')

	x6,y6 = [coords(x5-feedlength+wfeed+2*gfeed),coords(y5-bondh-2*feedlength-inlength)]
	feed += rt.feedbond(x6,y6,wfeed,gfeed,feedlength=feedlength,bondlength=bondlength,bondh=bondh,orientation='N')

	xcoords = [x0,x1,x2,x3,x4,x5,x6]
	ycoords = [y0,y1,y2,y3,y4,y5,y6]

	return feed, xcoords, ycoords

def quarterwave_resonator(xstart,ystart,wqw,gqw,rqw,lqw,wfeed,gfeed,coupling_gap):

	l1,l2,l3,l4,arc = section_lengths(wqw,gqw,rqw,lqw)

	xres00,yres00 = [coords(xstart,-gqw),coords(ystart,wfeed+2*gfeed+coupling_gap)]
	qw = [rs.rect(gqw,wqw+2*gqw,xres00,yres00)]

	xres0,yres0 = [coords(xstart),coords(ystart,wfeed+2*gfeed+coupling_gap)]
	qw += rs.straight_trench(l1, wqw, gqw, xres0, yres0, orientation='H')

	xres1,yres1 = [coords(xres0,l1),coords(yres0,rqw+wqw+2*gqw)]
	qw += rs.halfarc_trench(rqw, wqw, gqw, xres1, yres1, orient='E')

	xres2,yres2 = [coords(xres1),coords(yres1,rqw)]
	qw += rs.straight_trench(-l2, wqw, gqw, xres2, yres2, orientation='H')

	xres3,yres3 = [coords(xres2,-l2),coords(yres2,rqw+wqw+2*gqw)]
	qw += rs.halfarc_trench(rqw, wqw, gqw, xres3, yres3, orient='W')

	xres4,yres4 = [coords(xres3),coords(yres3,rqw)]
	qw += rs.straight_trench(l2, wqw, gqw, xres4, yres4, orientation='H')

	xres5,yres5 = [coords(xres4,l2),coords(yres4,rqw+wqw+2*gqw)]
	qw += rs.halfarc_trench(rqw, wqw, gqw, xres5, yres5, orient='E')

	xres6,yres6 = [coords(xres5),coords(yres5,rqw)]
	qw += rs.straight_trench(-l4, wqw, gqw, xres6, yres6, orientation='H')

	xres7,yres7 = [coords(xres6,-l4-gqw),coords(yres6)]
	qw += [rs.rect(gqw,wqw+2*gqw,xres7,yres7)]

	return qw

def DC_contacts_etch(x0, y0, w, l, bond, gap, contacts=4):
    x0 = float(x0)
    y0 = float(y0)
    shapes = []
    shapes += [rs.rect(4*bond + l + 4*gap, gap, x0, y0)]
    shapes += [rs.rect(gap, bond, x0, y0 + gap)]
    shapes += [rs.rect(bond*2 + gap*3, gap, x0, y0 + gap + bond)]
    shapes += [rs.rect(gap, bond - w, x0 + bond + gap, y0 + gap + w)]
    shapes += [rs.rect(bond - gap, gap, x0 + bond + 2* gap, y0 + gap + w)]
    shapes += [rs.rect(gap, bond, x0 + 2*bond + 2*gap, y0 + gap + w)]
    shapes += [rs.rect(l - 2*gap, gap, x0 + 2*bond + 3*gap, y0 + gap + w)]
    shapes += [rs.rect(gap, bond, x0 + 2*bond + gap + l, y0 + gap + w)]
    shapes += [rs.rect(2*bond + 2*gap, gap, x0 + 2*bond + 2*gap + l, y0 + gap + bond)]
    shapes += [rs.rect(gap, bond , x0 + 3*bond + 2*gap + l, y0 + gap + w)]
    shapes += [rs.rect(gap, bond + w , x0 + 4*bond + 3*gap + l, y0 + gap)]
    shapes += [rs.rect(bond - gap, gap, x0 + 2*bond + 3*gap+ l, y0 + gap + w)]
   
    # shapes = [move(i, x0, y0) for i in shapes]
   
    return shapes

feed,xc,yc = full_feedline(wfeed,gfeed,50,50)

for i in range(0,len(feed)):
	fd = gdspy.Polygon(feed[i],2)
	poly_cell.add(fd)

lqw = 4000
wqw = wfeed
gqw = gfeed
rqw = 150

coupling_gap = 50

qw1 = quarterwave_resonator(xc[3],yc[3],wqw,gqw,rqw,lqw,wfeed,gfeed,coupling_gap)

for i in range(0,len(qw1)):
	qwm = gdspy.Polygon(qw1[i],2)
	poly_cell.add(qwm)

qw2 = quarterwave_resonator(xc[4]-600,yc[3],wqw,gqw,rqw,lqw,wfeed,gfeed,coupling_gap)

for i in range(0,len(qw2)):
	qwm = gdspy.Polygon(qw2[i],2)
	poly_cell.add(qwm)	

wdc = 5
gdc = 13
ldc = 300
bond_dc = 400
xdc0 = sub_x/2 - 2*bond_dc -ldc/2 - gdc
ydc0 = 3800

dc = DC_contacts_etch(xdc0,ydc0,wdc,ldc,bond_dc,gdc,contacts=4)


for i in range(0,len(dc)):
	dcm = gdspy.Polygon(dc[i],2)
	poly_cell.add(dcm)	

###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
