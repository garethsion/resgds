#!/usr/bin/env python
import os
from resgds import *
import bragg
from interface import Interface
import gdspy # gds library
import numpy as np
from restempfiles import *

# hz_sweep = array([3318.42, 3368.42, 3418.42, 3468.42, 3518.42, 3568.42, 3618.42,
       # 3668.42, 3718.42, 3768.42, 3818.42])

# Layout filename
layout_file ='fab_files/exp_test.gds'

# CPW Parameters
###########################################################################
sub_x, sub_y = [4000, 9000] # substrate dimensions

coords = lambda x,dx=0: x+dx
xb_strt,yb_strt = [coords(1220),coords(2348.125)]

# Instantiate objects and creat geometry
###########################################################################
# Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)
rt = ResTempFiles(poly_cell)

# Substrate [layer 0]
sub = BuildRect(poly_cell, sub_x, sub_y, layer=0)
# sub.make(0,0)


# INPUT FEEDLINE
###############################################################################
length = 2000
width = 100
gap = 100

x0,y0 = [coords(0,100),coords(0,100)]
feed = rs.straight_trench(length,width,gap,x0,y0,orientation='V')

x1,y1 = [coords(x0,width + 2*gap + 200),coords(y0)]
feed += rs.straight_trench(length,width,gap,x1,y1,orientation='V')

x2,y2 = [coords(x1,width + 2*gap + 200),coords(y0)]
feed += rs.straight_trench(length,width,gap,x2,y2,orientation='V')

x3,y3 = [coords(x2,width + 2*gap + 200),coords(y0)]
feed += rs.straight_trench(length,width,gap,x3,y3,orientation='V')

x4,y4 = [coords(x3,width + 2*gap + 200),coords(y0)]
feed += rs.straight_trench(length,width,gap,x4,y4,orientation='V')

x5,y5 = [coords(x4,width + 2*gap + 200),coords(y0)]
feed += rs.straight_trench(length,width,gap,x5,y5,orientation='V')

x6,y6 = [coords(x5,width + 2*gap + 200),coords(y0)]
feed += rs.straight_trench(length,width,gap,x6,y6,orientation='V')

x7,y7 = [coords(x6,width + 2*gap + 200),coords(y0)]
feed += rs.straight_trench(length,width,gap,x7,y7,orientation='V')




x8,y8 = [coords(x0),coords(y0,length + 200)]
feed += rs.straight_trench(length,width,gap,x8,y8,orientation='V')

x9,y9 = [coords(x8,width + 2*gap + 200),coords(y8)]
feed += rs.straight_trench(length,width,gap,x9,y9,orientation='V')

x10,y10 = [coords(x9,width + 2*gap + 200),coords(y8)]
feed += rs.straight_trench(length,width,gap,x10,y10,orientation='V')

x11,y11 = [coords(x10,width + 2*gap + 200),coords(y8)]
feed += rs.straight_trench(length,width,gap,x11,y11,orientation='V')

x12,y12 = [coords(x11,width + 2*gap + 200),coords(y8)]
feed += rs.straight_trench(length,width,gap,x12,y12,orientation='V')

x13,y13 = [coords(x12,width + 2*gap + 200),coords(y8)]
feed += rs.straight_trench(length,width,gap,x13,y13,orientation='V')

x14,y14 = [coords(x13,width + 2*gap + 200),coords(y8)]
feed += rs.straight_trench(length,width,gap,x14,y14,orientation='V')

x15,y15 = [coords(x14,width + 2*gap + 200),coords(y8)]
feed += rs.straight_trench(length,width,gap,x15,y15,orientation='V')





x16,y16 = [coords(x0),coords(y8,length + 200)]
feed += rs.straight_trench(length,width,gap,x16,y16,orientation='V')

x17,y17 = [coords(x8,width + 2*gap + 200),coords(y16)]
feed += rs.straight_trench(length,width,gap,x17,y17,orientation='V')

x18,y18 = [coords(x9,width + 2*gap + 200),coords(y16)]
feed += rs.straight_trench(length,width,gap,x18,y18,orientation='V')

x19,y19 = [coords(x10,width + 2*gap + 200),coords(y16)]
feed += rs.straight_trench(length,width,gap,x19,y19,orientation='V')

x20,y20 = [coords(x11,width + 2*gap + 200),coords(y16)]
feed += rs.straight_trench(length,width,gap,x20,y20,orientation='V')

x21,y21 = [coords(x12,width + 2*gap + 200),coords(y16)]
feed += rs.straight_trench(length,width,gap,x21,y21,orientation='V')

x22,y22 = [coords(x13,width + 2*gap + 200),coords(y16)]
feed += rs.straight_trench(length,width,gap,x22,y22,orientation='V')

x23,y23 = [coords(x14,width + 2*gap + 200),coords(y16)]
feed += rs.straight_trench(length,width,gap,x23,y23,orientation='V')





x24,y24 = [coords(x0),coords(y23,length + 200)]
feed += rs.straight_trench(length,width,gap,x24,y24,orientation='V')

x25,y25 = [coords(x24,width + 2*gap + 200),coords(y24)]
feed += rs.straight_trench(length,width,gap,x25,y25,orientation='V')

x26,y26 = [coords(x25,width + 2*gap + 200),coords(y24)]
feed += rs.straight_trench(length,width,gap,x26,y26,orientation='V')

x27,y27 = [coords(x26,width + 2*gap + 200),coords(y24)]
feed += rs.straight_trench(length,width,gap,x27,y27,orientation='V')

x28,y28 = [coords(x27,width + 2*gap + 200),coords(y24)]
feed += rs.straight_trench(length,width,gap,x28,y28,orientation='V')

x29,y29 = [coords(x28,width + 2*gap + 200),coords(y24)]
feed += rs.straight_trench(length,width,gap,x29,y29,orientation='V')

x30,y30 = [coords(x29,width + 2*gap + 200),coords(y24)]
feed += rs.straight_trench(length,width,gap,x30,y30,orientation='V')

x31,y31 = [coords(x30,width + 2*gap + 200),coords(y24)]
feed += rs.straight_trench(length,width,gap,x31,y31,orientation='V')

# x1,y1 = [coords(x0 - rlow),coords(y0,-lf1)]
# feed += rs.halfarc_trench(rlow,wcav,gcav,x1,y1,orient='S')

# x2,y2 = [coords(x1,-rlow-wlow-2*glow),coords(y1)]
# feed += rs.straight_trench(lf2+15,wcav,gcav,x2,y2,orientation='V')

# x3,y3 = [coords(x2,-rqarc),coords(y2,lf2+15)]
# feed += rs.quarterarc_trench(rqarc,wcav,gcav,x3,y3,orient='NE')

# x4,y4 = [coords(x3,-lf3),coords(y3,rqarc)]
# feed += rs.straight_trench(lf3,wcav,gcav,x4,y4,orientation='H')

# feed += rt.feedbond(x4,y4,wcav,gcav,feedlength=300,bondlength=600,bondh=150,orientation='E')

for i in range(0,len(feed)):
	fd = gdspy.Polygon(feed[i],1)
	poly_cell.add(fd)


###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)