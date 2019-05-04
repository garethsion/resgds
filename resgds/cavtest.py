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
import bragg
from interface import Interface
import gdspy # gds library
import numpy as np


# Layout filename
layout_file ='Cavity_test.gds'

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

# Select polarity of the mirrors
###################################################################
w1,g1 = [whigh,ghigh]
w2,g2 = [wlow,glow]

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

taper_length = 80
lcav1 = 2000
lcav2 = lc-2*(lcav1+taper_length-2*rharc*np.pi)

cav_xtaper, cav_ytaper = [coords(x0),coords(y0)]
xr = x0 + 2*glow + wlow
taperL = [ (x0,y0+taper_length), (x0+glow, y0+taper_length), (x0+gc,y0),(x0,y0)]
taperR = [ (xr,y0+taper_length), (xr-glow, y0+taper_length), (xr-gc,y0),(xr,y0)]
cav = [taperL,taperR]

cav_x0,cav_y0 = [coords(x0),coords(y0,-lcav1-taper_length)]
cav += rs.straight_trench(lcav1+taper_length,wc,gc, cav_x0, cav_y0, orientation='V')

cav_x1,cav_y1 = [coords(cav_x0,-rharc),coords(cav_y0,)]
cav += rs.halfarc_trench(rharc,wc,gc,cav_x1,cav_y1,orient='S',npoints=40)

cav_x2,cav_y2 = [coords(cav_x1,-rharc-wtot),coords(cav_y1)]
cav += rs.straight_trench(lcav2,wc,gc,cav_x2,cav_y2,orientation='V')

cav_x3,cav_y3 = [coords(cav_x2,rharc+wtot),coords(cav_y2,lcav2)]
cav += rs.halfarc_trench(rharc,wc,gc,cav_x3,cav_y3,orient='N',npoints=40)

cav_x4,cav_y4 = [coords(cav_x3,rharc),coords(cav_y3)]
cav += rs.straight_trench(-lcav1-taper_length,wc,gc, cav_x4, cav_y4, orientation='V')

cav_x5,cav_y5 = [coords(cav_x4),coords(cav_y4,-lcav1-taper_length)]
taperL = [ (cav_x5,cav_y5-taper_length), (cav_x5+glow, cav_y5-taper_length), (cav_x5+gc,cav_y5),(cav_x5,cav_y5)]
taperR = [ (xr,cav_y5-taper_length), (xr-glow, cav_y5-taper_length), (xr-gc,cav_y5),(xr,cav_y5)]
cav += [taperL,taperR]


for i in range(0,len(cav)):
	cavity = gdspy.Polygon(cav[i],cond_layer)
	# conductor = gdspy.fast_boolean(conductor,cavity, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(cavity)


# cav_x6,cav_y6 = [coords(cav_x5),coords(cav_y5,rqarc-2*gc-wc)]
# cavity.straight_trench(-lcav3,cav_x6,cav_y6,orient='H')

# cav_x7,cav_y7 = [coords(cav_x6-lcav3),coords(cav_y6+rqarc+2*glow+wlow)]
# cavity.quarterarc_trench(rqarc,cav_x7,cav_y7,orient='SW',npoints=40)

# cav_x8,cav_y8 = [coords(cav_x7,-rqarc-2*glow - wlow),coords(cav_y7)]
# cavity.straight_trench(lcav2,cav_x8,cav_y8,orient='V')

# cav_x9,cav_y9 = [coords(cav_x8,rlow+2*glow+wlow),coords(cav_y8,lcav2)]
# cavity.halfarc_trench(rlow,cav_x9,cav_y9,orient='N',npoints=40)

# cav_x10,cav_y10 = [coords(cav_x9,rlow),coords(cav_y9)]
# cavend = cavity.straight_trench(-lcav1+taper_length,cav_x10,cav_y10,orient='V')

# cavity.taper(wlow, glow, wc, gc, cav_x10, 
#        cav_y10-lcav1, cav_x10, cav_y10-lcav1+taper_length)


###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
