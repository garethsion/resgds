#!/usr/bin/env python
import os
from resgds import *
import bragg
from interface import Interface
import gdspy # gds library
import numpy as np
from restempfiles import *

# Layout filename
layout_file ='kinetic_bragg.gds'

# CPW Parameters
###########################################################################
sub_x, sub_y = [9000, 4000] # substrate dimensions
lcav,wcav,gcav = [8102.64, 21.60, 11.10]
lhigh,whigh,ghigh = [3566.62, 7.80, 18.00] 
llow,wlow,glow = [4091.32, 36.60, 3.60]

rlow,rhigh = [50,50]
rqarc = 100

coords = lambda x,dx=0: x+dx
xb_strt,yb_strt = [coords(sub_x/4 - 2000),coords(sub_y - 1500)]

# Instantiate objects and creat geometry
###########################################################################
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


highZ = bragg.Bragg(whigh, ghigh, lhigh, poly_cell, radius=rhigh, layer=2)
lowZ = bragg.Bragg(wlow, glow, llow, poly_cell, radius=rlow, layer=2)

cavity = bragg.Bragg(wcav, gcav, lcav/2, poly_cell, radius=rlow, layer=2)

no_periods = 12
n_left = 5
n_cav = 2
n_right = 5

arr_l = np.repeat(np.arange(0,int(no_periods)),2*np.ones(int(no_periods),dtype=int))
arr_h = np.append(arr_l[1:],[int(no_periods)], axis=0)

arr_l = np.delete(arr_l,[0,1])
arr_h = np.delete(arr_h,[0,1])

x = [xb_strt + arr_h[i]*highZ.mirror_width() + arr_l[i]*lowZ.mirror_width() for i in range(len(arr_h))]

cnt = 0
for i in range (0,n_left):
	lowZ.mirror(x[cnt], yb_strt, w_remove=wcav, g_remove=gcav)
	highZ.mirror(x[cnt+1], yb_strt, w_remove=wcav, g_remove=gcav)
	cnt = cnt + 2

cavity.mirror(x[cnt], yb_strt, w_remove=wcav, g_remove=gcav)
cavity.mirror(x[cnt+1], yb_strt, w_remove=wcav, g_remove=gcav)
cnt = cnt + 2

for i in range (0,n_right):
	highZ.mirror(x[cnt], yb_strt, w_remove=wcav, g_remove=gcav)
	lowZ.mirror(x[cnt+1], yb_strt, w_remove=wcav, g_remove=gcav)
	cnt = cnt + 2


# INPUT FEEDLINE
###############################################################################
lf1 = 1000
lf2 = 500
lf3 = 250

x0,y0 = [coords(x[0]),coords(yb_strt)]
feed = rs.straight_trench(-lf1,wcav,gcav,x0,y0,orientation='V')

x1,y1 = [coords(x0 - rlow),coords(y0,-lf1)]
feed += rs.halfarc_trench(rlow,wcav,gcav,x1,y1,orient='S')

x2,y2 = [coords(x1,-rlow-wlow-2*glow),coords(y1)]
feed += rs.straight_trench(lf2,wcav,gcav,x2,y2,orientation='V')

x3,y3 = [coords(x2,-rqarc),coords(y2,lf2)]
feed += rs.quarterarc_trench(rqarc,wcav,gcav,x3,y3,orient='NE')

x4,y4 = [coords(x3,-lf3),coords(y3,rqarc)]
feed += rs.straight_trench(lf3,wcav,gcav,x4,y4,orientation='H')

feed += rt.feedbond(x4,y4,wcav,gcav,feedlength=300,bondlength=600,bondh=150,orientation='E')

for i in range(0,len(feed)):
	fd = gdspy.Polygon(feed[i],2)
	poly_cell.add(fd)


# OUTPUT FEEDLINE
###############################################################################
x0,y0 = [coords(x[len(x)-1]+highZ.mirror_width()),coords(yb_strt)]
feed = rs.straight_trench(lf2,wcav,gcav,x0,y0,orientation='V')

x1,y1 = [coords(x0, rlow + wlow + 2*glow),coords(y0,lf2)]
feed += rs.halfarc_trench(rlow,wcav,gcav,x1,y1,orient='N')

x2,y2 = [coords(x1,rlow),coords(y1)]
feed += rs.straight_trench(-lf1,wcav,gcav,x2,y2,orientation='V')

x3,y3 = [coords(x2,rqarc+wlow+2*glow),coords(y2,-lf1)]
feed += rs.quarterarc_trench(rqarc,wcav,gcav,x3,y3,orient='SW')

x4,y4 = [coords(x3),coords(y3,-rqarc-wlow-2*glow)]
feed += rs.straight_trench(lf3,wcav,gcav,x4,y4,orientation='H')

feed += rt.feedbond(x4+lf3,y4,wcav,gcav,feedlength=300,bondlength=600,bondh=150,orientation='W')

for i in range(0,len(feed)):
	fd = gdspy.Polygon(feed[i],2)
	poly_cell.add(fd)

# # Make lower Bragg periods
# lowZ.mirror(x[0], yb_strt, w_remove=wcav, g_remove=gcav)
# highZ.mirror(x[1], yb_strt, w_remove=wcav, g_remove=gcav)

# lowZ.mirror(x[2], yb_strt, w_remove=wcav, g_remove=gcav)
# highZ.mirror(x[3], yb_strt, w_remove=wcav, g_remove=gcav)

# lowZ.mirror(x[4], yb_strt, w_remove=wcav, g_remove=gcav)
# highZ.mirror(x[5], yb_strt, w_remove=wcav, g_remove=gcav)

# lowZ.mirror(x[6], yb_strt, w_remove=wcav, g_remove=gcav)
# highZ.mirror(x[7], yb_strt, w_remove=wcav, g_remove=gcav)


# # Make lower Bragg periods
# lowZ.mirror(xb_strt + highZ.mirror_width()+ lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)
# highZ.mirror(xb_strt + 2*highZ.mirror_width()+ lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)

# lowZ.mirror(xb_strt + 2*highZ.mirror_width()+ 2*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)
# highZ.mirror(xb_strt + 3*highZ.mirror_width()+ 2*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)

# lowZ.mirror(xb_strt + 3*highZ.mirror_width()+ 3*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)
# highZ.mirror(xb_strt + 4*highZ.mirror_width()+ 3*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)

# lowZ.mirror(xb_strt + 4*highZ.mirror_width()+ 4*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)
# highZ.mirror(xb_strt + 5*highZ.mirror_width()+ 4*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)

# lowZ.mirror(xb_strt + 5*highZ.mirror_width()+ 5*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)
# highZ.mirror(xb_strt + 6*highZ.mirror_width()+ 5*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)


# cavity.mirror(xb_strt + 6*highZ.mirror_width()+ 6*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)
# cavity.mirror(xb_strt + 7*highZ.mirror_width()+ 6*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)

# # Make lower Bragg periods
# highZ.mirror(xb_strt + 7*highZ.mirror_width()+ 7*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)
# lowZ.mirror(xb_strt + 8*highZ.mirror_width()+ 7*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)

# highZ.mirror(xb_strt + 8*highZ.mirror_width()+ 8*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)
# lowZ.mirror(xb_strt + 9*highZ.mirror_width()+ 8*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)

# highZ.mirror(xb_strt + 9*highZ.mirror_width()+ 9*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)
# lowZ.mirror(xb_strt + 10*highZ.mirror_width()+ 9*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)

# highZ.mirror(xb_strt + 10*highZ.mirror_width()+ 10*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)
# lowZ.mirror(xb_strt + 11*highZ.mirror_width()+ 10*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)

# highZ.mirror(xb_strt + 11*highZ.mirror_width()+ 11*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)
# lowZ.mirror(xb_strt + 12*highZ.mirror_width()+ 11*lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)





# x0,y0 = [coords(xb_strt),coords(yb_strt)]
# feed = rs.straight_trench(-500,wlow,glow,x0,y0,orientation='V')

# for i in range(0,len(feed)):
# 	fd = gdspy.Polygon(feed[i],2)
# 	poly_cell.add(fd)



# FEEDLINES - INPUT
#####################################################################

# highZ.mirror(xb_strt - lowZ.mirror_width(), yb_strt, w_remove=wcav, g_remove=gcav)

# x0 = xb_strt - lowZ.mirror_width()
# y0 = yb_strt

# feed = rs.straight_trench(-l3,wlow,glow,x0,y0,orientation='V')

# x1,y1 = [ coords(x0,-rlow), coords(y0,-l3) ]
# feed += rs.halfarc_trench(rlow,wlow,glow,x1,y1,orient='S')

# x2,y2 = [ coords(x1,-rlow-wlow-2*glow), coords(y1) ]
# feed += rs.straight_trench(l2-250+39,wlow,glow,x2,y2,orientation='V')

# x3,y3 = [ coords(x2,-rlow), coords(y2,l2-250+39) ]
# feed += rs.halfarc_trench(rlow,wlow,glow,x3,y3,orient='N')

# x4,y4 = [ coords(x3,-rlow-wlow-2*glow), coords(y3) ]
# feed += rs.straight_trench(-l1-250+39,wlow,glow,x4,y4,orientation='V')

# x5,y5 = [ coords(x4,-rlow), coords(y4,-l1-250+39) ]
# feed += rs.quarterarc_trench(rlow,wlow,glow,x5,y5,orient='SE')

# x6,y6 = [ coords(x5), coords(y5,-rlow-wlow-2*glow) ]
# feed += rs.straight_trench(-300,wlow,glow,x6,y6,orientation='H')

# feed += rt.feedbond(x6-300,y6,wlow,glow,feedlength=300,bondlength=600,bondh=150,orientation='E')


###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)