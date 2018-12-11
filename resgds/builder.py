#!/usr/bin/env python
import os
from resgds import *
import bragg
from interface import Interface
import gdspy # gds library
import numpy as np
#from subprocess import call # Use to call kaloput_viewer bash script
#import psutil # Use to check if klayout is running already

# Layout filename
layout_file = 'builder.gds'

# Parameters
#__________________________________________________________
sub_x, sub_y = [4000, 9000] # substrate dimensions
wc, gc, lc = [8.11, 17.85, 8108.45] # Cavity width, gap, length
wlow, llow = [30.44, 4051.32]  # Low Z section
whigh, lhigh = [2, 4051.32] # High Z section
glow, ghigh = [.5*(wc + 2*gc - wlow),.5*(wc + 2*gc - whigh)]

rext, rlow, rhigh = [0, 55, 55] # radii

lext1, lext2 = [400, 1200] # Extrude lengths
lext3 = llow - lext1 - lext2 - 500*np.pi - 150*np.pi

# Start making resonator geometry
#__________________________________________________________

# Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# Substrate [layer 0]
sub = BuildRect(poly_cell, sub_x, sub_y, layer=0)
sub.make(0,0)

# Antidot array [layer 1]
layout = LayoutComponents(poly_cell, sub_x, sub_y,layer=1)
layout.make_antidot_array(0,0,10,30,0)

# Cavity [layer 2]
# I assign coordinates first, and then build geometries accordingly
#
coords = lambda x,dx=0: x+dx
xb_strt,yb_strt = [coords(400),coords(sub_y/2)- lext2 - lext3 - 100]
lcav1, lcav2, lcav3 = [1000, 5500, 1000]

cavity = Trench(wc, gc, poly_cell, layer = 2)

cav_x0,cav_y0 = [coords(xb_strt),coords(yb_strt,-lcav1)]
cavity.straight_trench(lcav1, cav_x0, cav_y0, orient='V')

cav_x1,cav_y1 = [coords(xb_strt,-rlow),coords(yb_strt,-lcav1)]
cavity.halfarc_trench(rlow,cav_x1,cav_y1,orient='S',npoints=40)

cav_x2,cav_y2 = [coords(xb_strt,-2*rlow-wlow-2*glow),coords(yb_strt,-lcav1)]
cavity.straight_trench(lcav2,cav_x2,cav_y2,orient='V')

cav_x3,cav_y3 = [coords(xb_strt,-rlow),coords(yb_strt,lcav2-lcav1)]
cavity.halfarc_trench(rlow,cav_x3,cav_y3,orient='N',npoints=40)

cav_x4,cav_y4 = [coords(xb_strt),coords(yb_strt,lcav2-lcav1-lcav3)]
cavend = cavity.straight_trench(lcav3,cav_x4,cav_y4,orient='V')

# Bragg Mirror Sections
#
no_periods = 5
highZ = bragg.Bragg(whigh, ghigh, lhigh, poly_cell, radius=rhigh, layer=2,remove_layer=None)
lowZ = bragg.Bragg(wlow, glow, llow, poly_cell, radius=rlow, layer=2, remove_layer = None)

# Vectors to store shifting numbers for making mirrors
arr_l = np.repeat(np.arange(0,no_periods),2*np.ones(no_periods,dtype=int))
arr_h = np.append(arr_l[1:],[no_periods], axis=0)

# Make lower Bragg periods
make_lowZ = lambda i: lowZ.mirror(xb_strt + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strt, w_remove=wc, g_remove=gc)
make_highZ = lambda i: highZ.mirror(xb_strt + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strt, w_remove=wc, g_remove=gc)
[make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 1]
[make_highZ(x) for x in range(len(arr_l)) if x % 2 == 0]




xb_strtr = xb_strt
yb_strtr = cavend[1][0][1]

# Make upper Bragg periods
make_lowZ = lambda i: lowZ.rotate_mirror2(xb_strtr + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strtr,w_remove=wc, g_remove=gc)
make_highZ = lambda i: highZ.rotate_mirror2(xb_strtr + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strtr,w_remove=wc, g_remove = gc)
[make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 1]
[make_highZ(x) for x in range(len(arr_l)) if x % 2 == 0]

# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
