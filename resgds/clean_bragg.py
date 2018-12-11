#!/usr/bin/env python

import os
from interface import Interface
from resgds import *
import bragg
import gdspy # gds library
import numpy as np
from subprocess import call # Use to call kaloput_viewer bash script
import psutil # Use to check if klayout is running already   

# Layout filename
layout_file = 'clean_bragg.gds'

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

# Cavity sections [layer 2]
#
coords = lambda x,dx=0: x+dx
xb_strt,yb_strt = [coords(400),coords(sub_y/2)- lext2 - lext3 - 100]

lcav1, lcav2, lcav3 = [1000, 5500, 1000]

cavity = Trench(wc, gc, poly_cell, layer = 2)

x0,y0 = [coords(xb_strt),coords(yb_strt,-lcav1)]
cavity.straight_trench(lcav1, x0, y0, orient='V')

x1,y1 = [coords(xb_strt,-rlow),coords(yb_strt,-lcav1)]
cavity.halfarc_trench(rlow,x1,y1,orient='S',npoints=40)

x2,y2 = [coords(xb_strt,-2*rlow-wlow-2*glow),coords(yb_strt,-lcav1)]
cavity.straight_trench(lcav2,x2,y2,orient='V')

x3,y3 = [coords(xb_strt,-rlow),coords(yb_strt,lcav2-lcav1)]
cavity.halfarc_trench(rlow,x3,y3,orient='N',npoints=40)

x4,y4 = [coords(xb_strt),coords(yb_strt,lcav2-lcav1-lcav3)]
cavend = cavity.straight_trench(lcav3,x4,y4,orient='V')

# Cavity Removes [layer 3]
#
rm_width = 4*wc + 2*gc

cavity_remove = BuildRect(poly_cell,rm_width, lcav1, layer = 3)
rms1 = cavity_remove.make(x0-rm_width/2 + wc/2+gc,y0,layer=3)

x2,y2 = [coords(xb_strt,-2*rlow-wlow-2*glow),coords(yb_strt,-lcav1)]
cavity_remove = BuildRect(poly_cell,rm_width, lcav2, layer = 3)
rms2 = cavity_remove.make(x2-rm_width/2 + wc/2+gc,y2,layer=3)

wdth = rms1[0][0] - rms2[0][0]
wdth2 = wdth/2 + rm_width/2

rhf1 = rs.make_halfarc(0, wdth2, rms2[1][0] + wdth2/2 - 12.65, y0, orientation='S', npoints=40,layer=3)
rhf2 = rs.make_halfarc(0, wdth2, rms2[1][0] + wdth2/2 - 12.65, y0+lcav2, orientation='N', npoints=40,layer=3)

cavity_remove = BuildRect(poly_cell,rm_width, lcav3, layer = 3)
rms3 = cavity_remove.make(x4-rm_width/2 + wc/2+gc,y4,layer=3)

# Bragg Mirror Sections [layer 2]
#
no_periods = 5

# Instantiate Bragg sections
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

xb_strtr = xb_strt
yb_strtr = cavend[1][0][1]

# Make upper Bragg periods
make_lowZ = lambda i: lowZ.rotate_mirror2(xb_strtr + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strtr) 
make_highZ = lambda i: highZ.rotate_mirror2(xb_strtr + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strtr) 
[make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 1]
[make_highZ(x) for x in range(len(arr_l)) if x % 2 == 0]

# Feedline [layer 2]
#

# Make feedline sections
cc, ratio, bond_pad, rfeed = [2*gc, .5, 200, 100]
feedin_length, feedlink_length = [100, 685]

feedline = Trench(wc,gc,poly_cell, layer=2)

xf0 = lowZ.get_mirror_coordinates()[1][0]
yf0 = lowZ.get_mirror_coordinates()[1][1]

xf1,yf1 = [coords(xf0,rfeed+2*gc+wc),coords(yf0)]
fht = feedline.halfarc_trench(rfeed,xf1, yf1,orient='N',npoints=40)
fht_strait = feedline.straight_trench(-1600,fht[0][0][0],fht[0][0][1],orient='V')

feed_rhs = LayoutComponents(poly_cell, fht_strait[0][3][0]-2*wc-4*gc, fht_strait[0][3][1], 
        width=wc, gap = gc, layer=2)
feedbond = feed_rhs.make_feedbond(feedin_length,cc, ratio, 
        bond_pad, fht_strait[0][3][0], fht_strait[0][3][1], orientation='N')

# Feedline removes [layer 3]
#
feed_remove = BuildRect(poly_cell,rm_width, -1600, layer = 3)
rms4 = feed_remove.make(xf1+rm_width + wc/2+gc,yf1,layer=3)
rms4_remove = feed_remove.make(xf1+rm_width + wc/2+gc,yf1-feedin_length,layer=3)

rhf3 = rs.make_halfarc(0, wdth+3, rms4[1][0]  - wdth2 -46.5, 
    rms4[1][1], orientation='N', npoints=40,layer=3)

xstr = rms4_remove[0][0]
ystr = rms4_remove[3][1]
xend = rms4_remove[2][0]

feed_remove = feed_rhs.make_feedbond_remove(feedin_length,cc, ratio, 
        bond_pad, fht_strait[0][3][0],fht_strait[0][3][1],xstr,ystr,xend, orientation='N')

# Rotated Feedline [layer 2]
#
xf0r = lowZ.get_rotated_mirror_coordinates()[1][0]
yf0r = lowZ.get_rotated_mirror_coordinates()[1][1]

npts = 40
xf1r,yf1r = [coords(xf0r,rfeed+2*gc+wc),coords(yf0r)]
fhtr = feedline.halfarc_trench(rfeed,xf1r, yf1r,orient='S',npoints=40)
fhtr_strait = feedline.straight_trench(1600,fhtr[0][npts-1][0],fhtr[0][0][1],orient='V')

feed_lhs = LayoutComponents(poly_cell, fhtr_strait[0][3][0]-2*wc-4*gc, fhtr_strait[0][3][1], 
        width=wc, gap = gc, layer=2)
feedbond = feed_lhs.make_feedbond(feedin_length,cc, ratio, 
        bond_pad, fhtr_strait[0][3][0], fhtr_strait[0][3][1], orientation='S')

# Rotated feedline removes [layer 3]
#
feedr_remove = BuildRect(poly_cell,rm_width, 1600, layer = 3)
rms5 = feedr_remove.make(xf1r+rm_width + wc/2+gc,yf1r,layer=3)

rhf3 = rs.make_halfarc(0, wdth+3, rms5[1][0]  - wdth2 -46.5, rms5[1][1], orientation='S', npoints=40,layer=3)

rms5_remove = feedr_remove.make(xf1r+rm_width + wc/2+gc,yf1r+feedin_length,layer=3)
xstr = rms5_remove[0][0]
ystr = rms5_remove[3][1]
xend = rms5_remove[2][0]

feed_remove = feed_lhs.make_feedbond_remove(feedin_length,cc, ratio, 
        bond_pad, fhtr_strait[0][3][0],fhtr_strait[0][3][1],xstr,ystr,xend, 'S')

# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
