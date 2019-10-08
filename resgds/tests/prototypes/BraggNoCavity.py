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
layout_file ='fab_files/BraggNoCavity.gds'

# Parameters
#__________________________________________________________
sub_x, sub_y = [9000, 4000] # substrate dimensions
wc, gc, lc = [8.11, 17.85, 8108.45] # Cavity width, gap, length
wlow, llow = [30.44, 4051.32]  # Low Z section
whigh, lhigh = [2, 4051.32] # High Z section
glow, ghigh = [.5*(wc + 2*gc - wlow),.5*(wc + 2*gc - whigh)]

rext, rlow, rhigh = [0, 55, 55] # radii
rqarc = 100

lext1, lext2 = [400, 1200] # Extrude lengths
lext3 = llow - lext1 - lext2 - 500*np.pi - 150*np.pi

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
layout.make_antidot_array(0,0,10,30,0)

# Cavity [layer 2]
# I assign coordinates first, and then build geometries accordingly
############################################################################
coords = lambda x,dx=0: x+dx
# xb_strt,yb_strt = [coords(725),coords(sub_y/2-997)]
xb_strt,yb_strt = [coords(sub_x/4-233),coords(sub_y - 1500)]

lcav1, lcav2, lcav3 = [377.5, 1100, 1900.5]
taper_length = 80

# Bragg Mirror Sections [layer 2]
###########################################################################
no_periods = 8
highZ = bragg.Bragg(whigh, ghigh, lhigh, poly_cell, radius=rhigh, layer=2)
lowZ = bragg.Bragg(wlow, glow, llow, poly_cell, radius=rlow, layer=2)

# Vectors to store shifting numbers for making mirrors
arr_l = np.repeat(np.arange(0,int(no_periods/2)),2*np.ones(int(no_periods/2),dtype=int))
arr_h = np.append(arr_l[1:],[int(no_periods/2)], axis=0)

# Make lower Bragg periods
make_lowZ = lambda i: lowZ.mirror(xb_strt + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strt, w_remove=wc, g_remove=gc)

make_highZ = lambda i: highZ.mirror(xb_strt + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strt, w_remove=wc, g_remove=gc)

[make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 0]
[make_highZ(x) for x in range(len(arr_l)) if x % 2 == 1]

arr_l = np.repeat(np.arange(int(no_periods/2),no_periods),2*np.ones(int(no_periods/2),dtype=int))
arr_h = np.append(arr_l[1:],[no_periods], axis=0)

[make_highZ(x) for x in range(len(arr_l)) if x % 2 == 0]
[make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 1]

# Lower feed sections 
#
l1, l2, l3, arc = highZ.section_lengths(wc,gc)
cc, ratio, bond_pad, rfeed = [2*ghigh, .5, 400, 100]
feedin_length, feedlink_length, feed_st_length = [100,685,1600]
# rstrt = rlow + 100
# rlow = 100

# FEEDLINES - INPUT
#####################################################################

highZ.mirror(xb_strt - lowZ.mirror_width(), yb_strt, w_remove=wc, g_remove=gc)

x0 = xb_strt - lowZ.mirror_width()
y0 = yb_strt

feed = rs.straight_trench(-l3,wlow,glow,x0,y0,orientation='V')

x1,y1 = [ coords(x0,-rlow), coords(y0,-l3) ]
feed += rs.halfarc_trench(rlow,wlow,glow,x1,y1,orient='S')

x2,y2 = [ coords(x1,-rlow-wlow-2*glow), coords(y1) ]
feed += rs.straight_trench(l2-250+39,wlow,glow,x2,y2,orientation='V')

x3,y3 = [ coords(x2,-rlow), coords(y2,l2-250+39) ]
feed += rs.halfarc_trench(rlow,wlow,glow,x3,y3,orient='N')

x4,y4 = [ coords(x3,-rlow-wlow-2*glow), coords(y3) ]
feed += rs.straight_trench(-l1-250+39,wlow,glow,x4,y4,orientation='V')

x5,y5 = [ coords(x4,-rlow), coords(y4,-l1-250+39) ]
feed += rs.quarterarc_trench(rlow,wlow,glow,x5,y5,orient='SE')

x6,y6 = [ coords(x5), coords(y5,-rlow-wlow-2*glow) ]
feed += rs.straight_trench(-300,wlow,glow,x6,y6,orientation='H')

feed += rt.feedbond(x6-300,y6,wlow,glow,feedlength=300,bondlength=600,bondh=150,orientation='E')


# FEEDLINES - OUTPUT
#####################################################################
highZ.mirror(xb_strt + (2*no_periods)*lowZ.mirror_width(), yb_strt, w_remove=wc, g_remove=gc)

x5 = xb_strt + (2*no_periods+1)*lowZ.mirror_width()
y5 = yb_strt

feed += rs.straight_trench(l1,wlow,glow,x5,y5,orientation='V')

x6,y6 = [ coords(x5,rlow+wlow+2*glow), coords(y5,l1) ]
feed += rs.halfarc_trench(rlow,wlow,glow,x6,y6,orient='N')

# le = -l2+arc/2+300

x7,y7 = [ coords(x6,rlow), coords(y6) ]
feed += rs.straight_trench(-l2,wlow,glow,x7,y7,orientation='V')

x8,y8 = [ coords(x7,rlow+wlow+2*glow), coords(y7,-l2) ]
feed += rs.halfarc_trench(rlow,wlow,glow,x8,y8,orient='S')

x9,y9 = [ coords(x8,rlow), coords(y8) ]
feed += rs.straight_trench(l1,wlow,glow,x9,y9,orientation='V')

x10,y10 = [ coords(x9,rlow+wlow+2*glow), coords(y9,l1) ]
feed += rs.quarterarc_trench(rlow,wlow,glow,x10,y10,orient='NW')

x11,y11 = [ coords(x10), coords(y10,rlow) ]
feed += rs.straight_trench(300,wlow,glow,x11,y11,orientation='H')

feed += rt.feedbond(x11+300,y11,wlow,glow,feedlength=300,bondlength=600,bondh=150,orientation='W')

for i in range(0,len(feed)):
	fd = gdspy.Polygon(feed[i],2)
	poly_cell.add(fd)


# FEEDLINE REMOVES - INPUT
#####################################################################
rm_width = 4*wc + 2*gc
arcrad = .5*(2*rlow - gc - wc)
x0r = x0+wlow/2+glow-rm_width/2
y0r = y0

feedr = [rs.rect(rm_width,-l3,x0r,y0r)]

x1r,y1r = [ coords(x0r,-arcrad), coords(y0r,-l3) ]
feedr += [rs.halfarc(arcrad,rm_width,x1r,y1r,orientation='S')]

x2r,y2r = [ coords(x1r,-arcrad-rm_width), coords(y1r) ]
feedr += [rs.rect(rm_width,l2-250+39,x2r,y2r)]

x3r,y3r = [ coords(x2r,-arcrad), coords(y2r,l2-250+39) ]
feedr += [rs.halfarc(arcrad,rm_width,x3r,y3r,orientation='N')]

x4r,y4r = [ coords(x3r,-arcrad-rm_width), coords(y3r) ]
feedr += [rs.rect(rm_width,-l1-250+39,x4r,y4r)]

x5r,y5r = [ coords(x4r,-arcrad), coords(y4r,-l1-250+39) ]
feedr += [rs.quarterarc(arcrad,rm_width,x5r,y5r,orientation='SE')]

x6r,y6r = [ coords(x5r), coords(y5r,-arcrad-rm_width) ]
feedr += [rs.rect(-300,rm_width,x6r,y6r)]

feedr += rt.feedbond_remove(x6r-300,y6r+rm_width/2-wlow/2-glow,wc,gc,feedlength=300,bondlength=600,bondh=150,orientation='E')

# FEEDLINE REMOVES - OUTPUT
#####################################################################

x5r = x5+wlow/2+glow-rm_width/2
y5r = y5

feedr += [rs.rect(rm_width,l1,x5r,y5r)]

x6r,y6r = [ coords(x5r,arcrad+rm_width), coords(y5r,l1) ]
feedr += [rs.halfarc(arcrad,rm_width,x6r,y6r,orientation='N')]

x7r,y7r = [ coords(x6r,arcrad), coords(y6r) ]
feedr += [rs.rect(rm_width,-l2,x7r,y7r)]

x8r,y8r = [ coords(x7r,arcrad+rm_width), coords(y7r,-l2) ]
feedr += [rs.halfarc(arcrad,rm_width,x8r,y8r,orientation='S')]

x9r,y9r = [ coords(x8r,arcrad), coords(y8r) ]
feedr += [rs.rect(rm_width,l1,x9r,y9r)]

x10r,y10r = [ coords(x9r,arcrad+rm_width), coords(y9r,l1) ]
feedr += [rs.quarterarc(arcrad,rm_width,x10r,y10r,orientation='NW')]

x11r,y11r = [ coords(x10r), coords(y10r,arcrad) ]
feedr += [rs.rect(300,rm_width,x11r,y11r)]

feedr += rt.feedbond_remove(x11r+300,y11r+rm_width/2-wlow/2-glow,wc,gc,feedlength=300,bondlength=600,bondh=150,orientation='W')


for i in range(0,len(feedr)):
	fdr = gdspy.Polygon(feedr[i],3)
	poly_cell.add(fdr)


###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
