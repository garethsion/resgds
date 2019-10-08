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
layout_file ='fab_files/bragg_3568.gds'

# CPW Parameters
###########################################################################
sub_x, sub_y = [9000, 4000] # substrate dimensions
lcav,wcav,gcav = [8102.64, 21.60, 11.10]
lhigh,whigh,ghigh = [3568.42, 7.80, 18.00] 
llow,wlow,glow = [4090.68, 36.60, 3.60]

rlow,rhigh = [40,40]
rqarc = 100

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
sub.make(0,0)

# Antidot array [layer 1]
layout = LayoutComponents(poly_cell, sub_x, sub_y,layer=1)
layout.make_antidot_array(0,0,5,15,0)

# marker = [rs.rect(100,100,100,500)]
marker = [rs.circ_arc(50, 200, 500, n=50, theta0=0, thetaf=2*np.pi)]
marker += [rs.circ_arc(50, 350, 500, n=50, theta0=0, thetaf=2*np.pi)]
marker += [rs.circ_arc(50, 500, 500, n=50, theta0=0, thetaf=2*np.pi)]
marker += [rs.circ_arc(50, 650, 500, n=50, theta0=0, thetaf=2*np.pi)]
marker += [rs.circ_arc(50, 800, 500, n=50, theta0=0, thetaf=2*np.pi)]
marker += [rs.circ_arc(50, 200, 300, n=50, theta0=0, thetaf=2*np.pi)]
for i in range(0,len(marker)):
	mkr = gdspy.Polygon(marker[i],4)
	poly_cell.add(mkr)


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
feed += rs.straight_trench(lf2+15,wcav,gcav,x2,y2,orientation='V')

x3,y3 = [coords(x2,-rqarc),coords(y2,lf2+15)]
feed += rs.quarterarc_trench(rqarc,wcav,gcav,x3,y3,orient='NE')

x4,y4 = [coords(x3,-lf3),coords(y3,rqarc)]
feed += rs.straight_trench(lf3,wcav,gcav,x4,y4,orientation='H')

feed += rt.feedbond(x4,y4,wcav,gcav,feedlength=300,bondlength=600,bondh=150,orientation='E')

for i in range(0,len(feed)):
	fd = gdspy.Polygon(feed[i],2)
	poly_cell.add(fd)


# INPUT FEEDLINE REMOVES
###############################################################################
rm_width = 4*wcav + 2*gcav
arcrad = .5*(2*rlow - rm_width/2 - .25*wlow)
arcrad_qarc = .5*(2*rqarc - rm_width/2 - .5*wcav)

x0r,y0r = [coords(x[0]+wcav/2+gcav-rm_width/2),coords(yb_strt)]
feedr = [rs.rect(rm_width,-lf1,x0r,y0r)]

x1r,y1r = [coords(x0r,-arcrad),coords(y0,-lf1)]
feedr += [rs.halfarc(arcrad,rm_width,x1r,y1r,orientation='S')]

x2r,y2r = [coords(x1r,-arcrad-rm_width),coords(y1r)]
feedr += [rs.rect(rm_width,lf2+15,x2r,y2r)]

x3r,y3r = [coords(x2r,-arcrad_qarc),coords(y2r,lf2+15)]
feedr += [rs.quarterarc(arcrad_qarc,rm_width,x3r,y3r,orientation='NE')]

x4r,y4r = [coords(x3r,-lf3),coords(y3r,arcrad_qarc)]
feedr += [rs.rect(lf3,rm_width,x4r,y4r)]

feedr += rt.feedbond_remove(x4r,y4r+rm_width/2-wlow/2-glow,wcav,gcav,feedlength=300,bondlength=600,bondh=150,orientation='E')

for i in range(0,len(feedr)):
	fdr = gdspy.Polygon(feedr[i],3)
	poly_cell.add(fdr)


# OUTPUT FEEDLINE
###############################################################################
x0,y0 = [coords(x[len(x)-1]+highZ.mirror_width()),coords(yb_strt)]
feed = rs.straight_trench(lf2,wcav,gcav,x0,y0,orientation='V')

x1,y1 = [coords(x0, rlow + wlow + 2*glow),coords(y0,lf2)]
feed += rs.halfarc_trench(rlow,wcav,gcav,x1,y1,orient='N')

x2,y2 = [coords(x1,rlow),coords(y1)]
feed += rs.straight_trench(-lf1+260,wcav,gcav,x2,y2,orientation='V')

x3,y3 = [coords(x2,rqarc+wlow+2*glow),coords(y2,-lf1+260)]
feed += rs.quarterarc_trench(rqarc,wcav,gcav,x3,y3,orient='SW')

x4,y4 = [coords(x3),coords(y3,-rqarc-wlow-2*glow)]
feed += rs.straight_trench(lf3,wcav,gcav,x4,y4,orientation='H')

feed += rt.feedbond(x4+lf3,y4,wcav,gcav,feedlength=300,bondlength=600,bondh=150,orientation='W')

for i in range(0,len(feed)):
	fd = gdspy.Polygon(feed[i],2)
	poly_cell.add(fd)

# OUTPUT FEEDLINE REMOVES
###############################################################################

x0r,y0r = [coords(x[len(x)-1]+highZ.mirror_width()+wcav/2+gcav-rm_width/2),coords(yb_strt)]
feedr = [rs.rect(rm_width,lf2,x0r,y0r)]

x1r,y1r = [coords(x0r,arcrad+rm_width),coords(y0,lf2)]
feedr += [rs.halfarc(arcrad,rm_width,x1r,y1r,orientation='N')]

x2r,y2r = [coords(x1r,arcrad),coords(y1r)]
feedr += [rs.rect(rm_width,-lf1+260,x2r,y2r)]

x3r,y3r = [coords(x2r,arcrad_qarc+rm_width),coords(y2r,-lf1+260)]
feedr += [rs.quarterarc(arcrad_qarc,rm_width,x3r,y3r,orientation='SW')]

x4r,y4r = [coords(x3r),coords(y3r,-arcrad_qarc-rm_width)]
feedr += [rs.rect(lf3,rm_width,x4r,y4r)]

feedr += rt.feedbond_remove(x4r+lf3,y4r+rm_width/2-wlow/2-glow,wcav,gcav,feedlength=300,bondlength=600,bondh=150,orientation='W')

for i in range(0,len(feedr)):
	fdr = gdspy.Polygon(feedr[i],3)
	poly_cell.add(fdr)


###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)