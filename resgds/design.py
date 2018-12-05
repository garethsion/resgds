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
sub_x = 10000
sub_y = 10000

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
rlow = 200 # Radius of low impedance section
rhigh = 200 # Radius of high impedance section

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

# Centre Cavity [layer 2]
x0, y0 = [coords(sub_x/2, -lc/2), coords(sub_y/2, -2*(wc/2) - gc/2)]
x0r, y0r = [coords(sub_x, -x0), coords(y0,rlow+wlow+2*glow)]
cavity = Trench(wc, gc, poly_cell, layer=2)
cavity.straight_trench(lc, x0, y0, orient='H')

# Low Z extrudance from Cavity (LHS) [layer 2]
Zlow = Trench(wlow, glow, poly_cell, layer=2)
Zlow.halfarc_trench(rlow, x0, y0-rlow, orient='W', npoints=40)
Zlow.halfarc_trench(rlow, x0r, y0r, orient='E', npoints=40)

x1,y1 = [coords(x0), coords(y0,-2*rlow-2*glow-wlow)]
x1r,y1r = [coords(x0r,-lext1), coords(y0r,rlow)]
Zlow.straight_trench(lext1,x1,y1,orient='H')
Zlow.straight_trench(lext1,x1r,y1r,orient='H')

x2,y2 = [coords(x0,lext1), coords(y0,-2*rlow-wlow-2*glow)]
x2r,y2r = [coords(x1r), coords(y1r,2*glow+wlow)]
Zlow.quarterarc_trench(rext,x2,y2,orient='NE',npoints=20)
Zlow.quarterarc_trench(rext,x2r,y2r,orient='SW',npoints=20)

x3,y3 = [coords(x2),coords(y2,-lext2)]
x3r,y3r = [coords(x2r,-2*glow-wlow),coords(y2r)]
Zlow.straight_trench(lext2, x3, y3, orient='V')
Zlow.straight_trench(lext2, x3r, y3r, orient='V')

x4,y4 = [coords(x3, wlow + 2*glow + rlow),coords(y3)]
x4r,y4r = [coords(x3r,-rlow),coords(y3r,lext2)]
Zlow.halfarc_trench(rlow,x4,y4,orient='S',npoints=40)
Zlow.halfarc_trench(rlow,x4r,y4r,orient='N',npoints=40)

x5,y5 = [coords(x4,rlow),coords(y4)]
x5r,y5r = [coords(x4r,-rlow - 2*glow - wlow),coords(y4r,-lext3)]
Zlow.straight_trench(lext3, x5, y5, orient='V')
Zlow.straight_trench(lext3, x5r, y5r, orient='V')

# Bragg Mirror Sections [layer 2]
no_periods = 4

xb_strt,yb_strt = [coords(x5),coords(y5,lext3)]
xb_strtr,yb_strtr = [coords(x5r),coords(y5r)]

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

# Make upper Bragg periods
make_rotate_lowZ = lambda i: lowZ.rotate_mirror(xb_strtr - arr_h[i]*highZ.mirror_width()
        - arr_l[i]*lowZ.mirror_width(), yb_strtr) 
make_rotate_highZ = lambda i: highZ.rotate_mirror(xb_strtr - arr_h[i]*highZ.mirror_width()
        - arr_l[i]*lowZ.mirror_width(), yb_strtr) 
[make_rotate_lowZ(x) for x in range(len(arr_l)) if x % 2 == 1]
[make_rotate_highZ(x) for x in range(len(arr_l)) if x % 2 == 0]

# Make feedline sections
cc = 50
ratio = .5
bond_pad = 200
rfeed = 100

# Feedline
feedin_length = 691.045
feedlink_length = 885
feedline = Trench(wc,gc,poly_cell, layer=2)

xf0 = lowZ.get_mirror_coordinates()[1][0]
yf0 = lowZ.get_mirror_coordinates()[1][1]
feedline.straight_trench(feedlink_length, xf0, yf0, orient='V')

xf1,yf1 = [coords(xf0,rfeed+wc+2*gc),coords(yf0,feedlink_length)]
feedline.quarterarc_trench(rfeed,xf1, yf1,orient='NW',npoints=20)
feedline.straight_trench(feedin_length, xf1, yf1+rfeed, orient='H')

xf2, yf2 = [coords(xf1,feedin_length+bond_pad), coords(yf1)]

# Feedbond
feed = LayoutComponents(poly_cell, xf1, yf1, layer=2)
#feedbond = feed.make_feedbond(cc, ratio, bond_pad, xf2, yf2, orientation='H')
feedbond = feed.make_feedbond(cc, ratio, bond_pad, sub_x, yf2+bond_pad, orientation='H')

# Make LHS feedline
xf0r = lowZ.get_rotated_mirror_coordinates()[1][0]
yf0r = lowZ.get_rotated_mirror_coordinates()[1][1]
feedline.straight_trench(feedlink_length, xf0r, yf0r-feedlink_length, orient='V')

xf1r,yf1r = [coords(xf0r,-rfeed),coords(yf0r,-feedlink_length)]
feedline.quarterarc_trench(rfeed,xf1r, yf1r,orient='SE',npoints=20)
feedline.straight_trench(feedin_length, xf1r-feedin_length, yf1r-rfeed-2*gc-wc, orient='H')


# Check if klayout is already running. If not, write gds and open klayout. 
# If it is, just update the gds file
if("klayout" in (p.name() for p in psutil.process_iter())):
    #Write the pattern as a gds file
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
else:
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
    kl = call('./klayout_viewer %s' %layout_file,shell=True)

