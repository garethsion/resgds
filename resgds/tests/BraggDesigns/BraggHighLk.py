#!/usr/bin/env python
import os
from resgds import *
import bragg
from interface import Interface
import gdspy # gds library
import numpy as np
from restempfiles import *

# Layout filename
layout_file ='fab_files/bragg_high_lk.gds'

# CPW Parameters
###########################################################################
sub_x, sub_y = [9000, 4000] # substrate dimensions
# lcav,wcav,gcav = [3502.64, 4, 38]
# lhigh,whigh,ghigh = [1014.75, 2.5, 38.75] 
# llow,wlow,glow = [3516.64, 10, 35]

lcav,wcav,gcav = [3462.27, 4, 38]
lhigh,whigh,ghigh = [1003.05, 2.5, 38.75] 
llow,wlow,glow = [3476.07, 10, 35]


rlow,rhigh = [25,25]
rqarc = 100

taper_length = 30

coords = lambda x,dx=0: x+dx
xb_strt,yb_strt = [coords(1220-139),coords(2348.125)]
yb_strt2 = yb_strt
yb_strt = yb_strt - taper_length
rm_width = 4*wcav + 2*gcav

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

d1 = [(x[cnt], yb_strt), (x[cnt]+ghigh, yb_strt), (x[cnt]+gcav, yb_strt+taper_length), (x[cnt], yb_strt+taper_length)]
xt = x[cnt]+2*ghigh+whigh
d2 = [(xt, yb_strt), (xt-ghigh, yb_strt), 
	(xt-gcav, yb_strt+taper_length), (xt, yb_strt+taper_length)]

taper = [d1,d2]

for i in range(0,len(taper)):
	tap = gdspy.Polygon(taper[i],2)
	poly_cell.add(tap)

taper_remove = [rs.rect(rm_width,taper_length, x[cnt]+ghigh+whigh/2-rm_width/2, yb_strt)]

for i in range(0,len(taper_remove)):
	tapr = gdspy.Polygon(taper_remove[i],3)
	poly_cell.add(tapr)

cavity.mirror(x[cnt], yb_strt2, w_remove=wcav, g_remove=gcav)
cavity.mirror(x[cnt+1], yb_strt, w_remove=wcav, g_remove=gcav)
cnt = cnt + 2

d1 = [(x[cnt], yb_strt), (x[cnt]+gcav, yb_strt), (x[cnt]+ghigh, yb_strt+taper_length), (x[cnt], yb_strt+taper_length)]
xt = x[cnt]+2*ghigh+whigh
d2 = [(xt, yb_strt), (xt-gcav, yb_strt), 
	(xt-ghigh, yb_strt+taper_length), (xt, yb_strt+taper_length)]
taper = [d1,d2]

for i in range(0,len(taper)):
	tap = gdspy.Polygon(taper[i],2)
	poly_cell.add(tap)

taper_remove = [rs.rect(rm_width,-taper_length, x[cnt]+ghigh+whigh/2-rm_width/2, yb_strt+taper_length)]
for i in range(0,len(taper_remove)):
	tapr = gdspy.Polygon(taper_remove[i],3)
	poly_cell.add(tapr)

for i in range (0,n_right):
	highZ.mirror(x[cnt], yb_strt+taper_length, w_remove=wcav, g_remove=gcav)
	lowZ.mirror(x[cnt+1], yb_strt+taper_length, w_remove=wcav, g_remove=gcav)
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

# arcrad = .5*(2*rlow - rm_width/2 - .25*wlow)
arcrad_qarc = .5*(2*rqarc - rm_width/2 - .5*wcav) + 17
arcrad = rlow - 5.5
# arcrad_qarc = arcrad 

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