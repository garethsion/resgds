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

# Cavity removes [layer 3]
#
# Cavity Removes
rm_width = 4*wc + 2*gc
arcrad = .5*(2*rlow - gc - wc)

# Lower cevity extrude straight remove
cav_x0r, cav_y0r = [coords(cav_x0,-rm_width/2+wc/2+gc),coords(cav_y0)]
cavity_remove = BuildRect(poly_cell,rm_width, lcav1, layer = 3)
straight_remove_L = cavity_remove.make(cav_x0r,cav_y0r,layer=3)

# Centre cavity straight remove
cav_x1r, cav_y1r = [coords(cav_x0,-2*rlow-wlow-2*glow),coords(yb_strt,-lcav1)]
cavity_remove = BuildRect(poly_cell,rm_width, lcav2, layer = 3)
straight_remove_C = cavity_remove.make(cav_x1r,cav_y1r,layer=3)

# Upper cavity straight remove
cav_x2r, cav_y2r = [coords(cav_x4,-rm_width/2 + wc/2+gc),coords(cav_y4)]
cavity_remove = BuildRect(poly_cell,rm_width, lcav3, layer = 3)
straight_remove_U = cavity_remove.make(cav_x2r,cav_y2r,layer=3)

# Lower cavity halfarc remove
cav_xhfrL, cav_yhfrL = [coords(cav_x0r - rm_width + arcrad/2),coords(cav_y1)]
cav_harc_remove = rs.make_halfarc(arcrad, rm_width,
	cav_xhfrL, cav_yhfrL, orientation='S', npoints=40, layer=3) 

# Upper cavity halfarc remove
cav_xhfrU, cav_yhfrU = [coords(cav_x0r - rm_width + arcrad/2),coords(cav_y1,lcav2)]
cav_harc_remove = rs.make_halfarc(arcrad, rm_width,
	cav_xhfrU, cav_yhfrU, orientation='N', npoints=40, layer=3) 

# Bragg Mirror Sections [layer 2]
#
no_periods = 5
highZ = bragg.Bragg(whigh, ghigh, lhigh, poly_cell, radius=rhigh, layer=2)
lowZ = bragg.Bragg(wlow, glow, llow, poly_cell, radius=rlow, layer=2)

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

# Make upper Bragg periods
xb_strtr = xb_strt
yb_strtr = cavend[1][0][1]

make_lowZ = lambda i: lowZ.rotate_mirror2(xb_strtr + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strtr,w_remove=wc, g_remove=gc)

make_highZ = lambda i: highZ.rotate_mirror2(xb_strtr + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strtr,w_remove=wc, g_remove = gc)

[make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 1]
[make_highZ(x) for x in range(len(arr_l)) if x % 2 == 0]

# Feedline sections [layer 2]
#
#Lower feedline
cc, ratio, bond_pad, rfeed = [2*gc, .5, 200, 100]
feedin_length, feedlink_length, feed_straight = [100,685,1600]
xf0 = lowZ.get_mirror_coordinates()[1][0]
yf0 = lowZ.get_mirror_coordinates()[1][1]

feedline = Trench(wc,gc,poly_cell, layer=2)

xf1,yf1 = [coords(xf0,rfeed+2*gc+wc),coords(yf0)]
feed_harctrL = feedline.halfarc_trench(rfeed,xf1, yf1,orient='N',npoints=40)
fht_strait = feedline.straight_trench(-feed_straight,feed_harctrL[0][0][0],
	feed_harctrL[0][0][1],orient='V')

# Lower feedbond
feed_rhs = LayoutComponents(poly_cell, fht_strait[0][3][0]-2*wc-4*gc, 
	fht_strait[0][3][1], width=wc, gap = gc, layer=2)
feedbond = feed_rhs.make_feedbond(feedin_length,cc, ratio, 
        bond_pad, fht_strait[0][3][0], fht_strait[0][3][1], orientation='N')

# Upper feedline
xf0r = lowZ.get_rotated_mirror_coordinates()[1][0]
yf0r = lowZ.get_rotated_mirror_coordinates()[1][1]

xf1r,yf1r = [coords(xf0r,rfeed+2*gc+wc),coords(yf0r)]
feed_harctrU = feedline.halfarc_trench(rfeed,xf1r, yf1r,orient='S',npoints=40)
npts = int(np.shape(feed_harctrU)[1]/2)
fhtr_strait = feedline.straight_trench(1600,feed_harctrU[0][npts-1][0],
	feed_harctrU[0][0][1],orient='V')

# Upper feedbond
feed_lhs = LayoutComponents(poly_cell, fhtr_strait[0][3][0]-2*wc-4*gc, 
	fhtr_strait[0][3][1], width=wc, gap = gc, layer=2)
feedbond = feed_lhs.make_feedbond(feedin_length,cc, ratio, bond_pad, 
	fhtr_strait[0][3][0], fhtr_strait[0][3][1], orientation='S')

# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
