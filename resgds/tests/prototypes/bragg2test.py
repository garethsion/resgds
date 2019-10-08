#!/usr/bin/env python

""" 
This modification of the Bragg resonator generator has a smaller footprint. 
This is to make the fabrication process easier, since I have had problems with
fitting the device onto the 10x5 chips.

I have also endeavoured to clean up the fabrication file, because I became unhappy 
with how untidy the code was. this is the start of the refactoring process.
"""

import os
from resgds import *
# import braggresonator
from interface import Interface
import gdspy # gds library
import numpy as np


def bragg_mirror(w,g,r,l,x0,y0,cell):
        """
            Defines a quarterwave Bragg mirror section.
        """
        coords = lambda x,dx=0: x+dx
        
        l1, l2, l3, arc = lengths(w,g,r,l)
        rs = Shapes(cell)

        # Make Bragg mirror sections
        #
        bragg = rs.straight_trench(l1, w, g,x0, y0, orientation='V')

        x1,y1 = [coords(x0,w+2*g+r), coords(y0,l1)]
        bragg += rs.halfarc_trench(r, w, g, x1, y1, orient='N', npoints=40)

        x2,y2 = [coords(x1,r), coords(y1,-l2)]
        bragg += rs.straight_trench(l2,w,g,x2,y2,orientation='V')

        x3,y3 = [coords(x2,w+2*g+r), coords(y2)]
        bragg += rs.halfarc_trench(r, w,g,x3, y3, orient='S', npoints=40)

        x4,y4 = [coords(x3,r), coords(y3)] 
        bragg += rs.straight_trench(l3,w,g,x4,y4,orientation='V')

        return bragg

def bragg_mirror_remove(w,g,r,l,x0,y0,cell):
    # Make remove sections
    #
    rm_width = 4*w + 2*g
    l1, l2, l3, arc = lengths(w,g,r,l)
    arcrad = .5*(2*r - g - w)
    rs = Shapes(cell)

    xrm0, yrm0 = [coords(x0-rm_width/2 + w/2+g),coords(y0)]
    remove = [rs.rect(rm_width,l1, xrm0, yrm0)]

    xrm1, yrm1 = [coords(xrm0,arcrad+rm_width),coords(yrm0,l1)]
    remove += [rs.halfarc(arcrad, rm_width, xrm1, yrm1, 
    orientation='N', npoints=40)] 

    xrm2, yrm2 = [coords(xrm1,arcrad),coords(yrm1)]
    remove += [rs.rect(rm_width,-l2, xrm2,yrm2)]

    xrm3, yrm3 = [coords(xrm2,arcrad+rm_width),coords(yrm2,-l2)]
    remove += [rs.halfarc(arcrad, rm_width, xrm3, yrm3, 
    orientation='S', npoints=40)] 

    xrm4, yrm4 = [coords(xrm3,arcrad),coords(yrm3)]
    remove += [rs.rect(rm_width,l3, xrm4,yrm4)]

    return remove

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

def mirror_width(w,g,r):
        """
            Method which calculates the total width of the Bragg mirror half period 
        """
        width = 2*(w + 2*g + 2*r)
        return width

# Layout filename
layout_file ='Bragg_test.gds'

# Parameters
###################################################################
sub_x, sub_y = [4000, 9000] # substrate dimensions
wc, gc, lc = [8.11, 17.85, 8108.45] # Cavity width, gap, length
wlow, llow = [30.44, 4051.32]  # Low Z section
whigh, lhigh = [2, 4051.32] # High Z section
glow, ghigh = [.5*(wc + 2*gc - wlow),.5*(wc + 2*gc - whigh)]
wtot = 2*gc+wc

sub_layer = 0
dot_layer = 1
cond_layer = 2
remove_layer = 3

rharc = 55 # halfarc radius
rqarc = 100 # quarterarc radius

conductor = []

# Select polarity of the mirrors
###################################################################
w1,g1 = [whigh,ghigh]
w2,g2 = [wlow,glow]
l1,l2 = [lhigh,llow]

# Start making resonator geometry
############################################################################

# Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# Substrate [layer 0]
sub = [rs.rect(sub_x,sub_y,0,0)]

for i in range(0,len(sub)):
	sub = gdspy.Polygon(sub[i],sub_layer)
	# conductor = gdspy.fast_boolean(conductor,cavity, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(sub)

# Antidot array [layer 1]
layout = LayoutComponents(poly_cell, sub_x, sub_y,layer=dot_layer)
dots = layout.antidot_array(0,0,10,30,0)

for i in range(0,len(dots)):
	antidots = gdspy.Polygon(dots[i],dot_layer)
	# conductor = gdspy.fast_boolean(conductor,cavity, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(antidots)

# Cavity [layer 2]
# I assign coordinates first, and then build geometries accordingly
############################################################################
coords = lambda x,dx=0: x+dx
x0,y0 = [coords(725),coords(sub_y/2-997)]






# Bragg Mirrors
##########################################################################
no_periods = 4
bragg = bragg_mirror(w1,g1,rharc,l1,x0,y0,poly_cell)

bragg_rem = bragg_mirror_remove(wc,gc,rharc,l1,x0,y0,poly_cell)

for i in range(len(bragg)):
	braggs = gdspy.Polygon(bragg[i],cond_layer)
	poly_cell.add(braggs)


for i in range(len(bragg_rem)):
    braggr = gdspy.Polygon(bragg_rem[i],remove_layer)
    poly_cell.add(braggr)


#############################################################################
circuit = gdspy.fast_boolean(dots,conductor,'or',
	precision=1e-9, max_points=1000, layer=sub_layer)

# poly_cell.add(circuit)

###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
