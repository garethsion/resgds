#!/usr/bin/env python

import os
from resgds import *
import bragg
import gdspy # gds library
import numpy as np
from subprocess import call # Use to call kaloput_viewer bash script
import psutil # Use to check if klayout is running already   

# Layout filename
layout_file = 'bragg.gds'

# Parameters
sub_x = 4000
sub_y = 9000

wc = 8.11 # Conductor width of cavity
gc = 17.85 # Gap b/w conductor and substrate
lc = 8108.45 # Length of cavity

wlow = 30.44  # Width of low impedance section
glow = .5*(wc + 2*gc - wlow) # Gap of low impedance section
llow = 4051.32 # Length of low impedance section

whigh = 2 # 
ghigh = .5*(wlow + 2*glow - whigh)
lhigh = 4051.32

rext = 0 # extrude radius
rlow = 70 # Radius of low impedance section
rhigh = 70 # Radius of high impedance section

lext1 = 400 # Lengths of straigh extrude sections
lext2 = 1200

lext3 = llow - lext1 - lext2 - 500*np.pi - 150*np.pi

# Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# Substrate [layer 0]
sub = BuildRect(poly_cell, sub_x, sub_y, layer=0)
sub.make(0,0)

# Antidot array [layer 1]
layout = LayoutComponents(poly_cell, sub_x, sub_y,layer=1)
layout.make_antidot_array(0,0,10,30,0)

coords = lambda x,dx=0: x+dx

# Bragg Mirror Sections [layer 2]
no_periods = 4

xb_strt,yb_strt = [coords(700),coords(lext2,lext3)]

highZ = bragg.Bragg(whigh, ghigh, lhigh, poly_cell, radius=rhigh, layer=2)
lowZ = bragg.Bragg(wlow, glow, llow, poly_cell, radius=rlow, layer=2)

# Vectors to store shifting numbers for making mirrors
arr_l = np.repeat(np.arange(0,no_periods),2*np.ones(no_periods,dtype=int))
arr_h = np.append(arr_l[1:],[no_periods], axis=0)

# Make lower Bragg periods
make_lowZ = lambda i: lowZ.mirror(xb_strt + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strt) 
make_highZ = lambda i: highZ.mirror(xb_strt + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strt) 
[make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 1]
[make_highZ(x) for x in range(len(arr_l)) if x % 2 == 0]

# Make feedline sections
cc =2*gc
ratio = .5
bond_pad = 200
rfeed = 100

# Feedline
feedin_length = 491.045
feedlink_length = 685
feedline = Trench(wc,gc,poly_cell, layer=2)

xf0 = lowZ.get_mirror_coordinates()[1][0]
yf0 = lowZ.get_mirror_coordinates()[1][1]
feedline.straight_trench(feedlink_length, xf0, yf0, orient='V')

xf1,yf1 = [coords(xf0,rfeed+wc+2*gc),coords(yf0,feedlink_length)]
fqt = feedline.quarterarc_trench(rfeed,xf1, yf1,orient='NW',npoints=20)

# Check if klayout is already running. If not, write gds and open klayout. 
# If it is, just update the gds file
if("klayout" in (p.name() for p in psutil.process_iter())):
    #Write the pattern as a gds file
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
else:
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
    kl = call('./klayout_viewer %s' %layout_file,shell=True)

