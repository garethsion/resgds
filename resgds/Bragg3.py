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


# Layout filename
layout_file ='fab_files/Bragg3.gds'

# Parameters
#__________________________________________________________
sub_x, sub_y = [4000, 9000] # substrate dimensions
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
xb_strt,yb_strt = [coords(725),coords(sub_y/2-997)]

lcav1, lcav2, lcav3 = [377.5, 1100, 1900.5]
taper_length = 80

cavity = Trench(wc, gc, poly_cell, layer = 2)

cav_x0,cav_y0 = [coords(xb_strt),coords(yb_strt,-lcav1)]
strait = cavity.straight_trench(lcav1-taper_length, cav_x0, cav_y0, orient='V')

cav_xtaper, cav_ytaper = [coords(xb_strt),coords(yb_strt,-taper_length)]

cavity.taper(wc, gc, wlow, glow, cav_x0, 
        cav_y0+lcav1-taper_length, cav_x0, cav_y0+lcav1)

cav_x1,cav_y1 = [coords(xb_strt,-rlow),coords(yb_strt,-lcav1)]
cavity.halfarc_trench(rlow,cav_x1,cav_y1,orient='S',npoints=40)

cav_x2,cav_y2 = [coords(xb_strt,-2*rlow-wlow-2*glow),coords(yb_strt,-lcav1)]
cavity.straight_trench(lcav2,cav_x2,cav_y2,orient='V')

cav_x3,cav_y3 = [coords(cav_x2,rqarc+2*gc+wc),coords(cav_y2,lcav2)]
cavity.quarterarc_trench(rqarc,cav_x3,cav_y3,orient='NW',npoints=40)

cav_x4,cav_y4 = [coords(cav_x3),coords(yb_strt, lcav2-lcav1+rqarc)]
cavity.straight_trench(lcav3,cav_x4,cav_y4,orient='H')

cav_x5,cav_y5 = [coords(cav_x4,lcav3),coords(cav_y4+rlow+2*glow+wlow)]
cavity.halfarc_trench(rlow,cav_x5,cav_y5,orient='E',npoints=40)

cav_x6,cav_y6 = [coords(cav_x5),coords(cav_y5,rqarc-2*gc-wc)]
cavity.straight_trench(-lcav3,cav_x6,cav_y6,orient='H')

cav_x7,cav_y7 = [coords(cav_x6-lcav3),coords(cav_y6+rqarc+2*glow+wlow)]
cavity.quarterarc_trench(rqarc,cav_x7,cav_y7,orient='SW',npoints=40)

cav_x8,cav_y8 = [coords(cav_x7,-rqarc-2*glow - wlow),coords(cav_y7)]
cavity.straight_trench(lcav2,cav_x8,cav_y8,orient='V')

cav_x9,cav_y9 = [coords(cav_x8,rlow+2*glow+wlow),coords(cav_y8,lcav2)]
cavity.halfarc_trench(rlow,cav_x9,cav_y9,orient='N',npoints=40)

cav_x10,cav_y10 = [coords(cav_x9,rlow),coords(cav_y9)]
cavend = cavity.straight_trench(-lcav1+taper_length,cav_x10,cav_y10,orient='V')

cavity.taper(wlow, glow, wc, gc, cav_x10, 
       cav_y10-lcav1, cav_x10, cav_y10-lcav1+taper_length)


# # Cavity removes [layer 3]
# ############################################################################

# Cavity Removes
rm_width = 4*wc + 2*gc
arcrad = .5*(2*rlow - gc - wc)
arcrad_qarc = .5*(2*rqarc - gc - wc)

cav_x0r, cav_y0r = [coords(cav_x0,wc/2+gc-rm_width/2),coords(cav_y0)]
cavr = [rs.rect(rm_width, lcav1,cav_x0r,cav_y0r)]

cav_x1r, cav_y1r = [coords(cav_x0r,-arcrad),coords(cav_y0r)]
cavr += [rs.halfarc(arcrad,rm_width,cav_x1r,cav_y1r,npoints=40, orientation='S')]

cav_x2r,cav_y2r = [coords(cav_x1r,-arcrad-rm_width),coords(cav_y1r)]
cavr += [rs.rect(rm_width,lcav2,cav_x2r,cav_y2r)]

cav_x3r, cav_y3r = [coords(cav_x2r,arcrad_qarc+rm_width),coords(cav_y2r,lcav2)]
cavr += [rs.quarterarc(arcrad_qarc,rm_width,cav_x3r,cav_y3r,npoints=40, orientation='NW')]

cav_x4r,cav_y4r = [coords(cav_x3r),coords(cav_y3r,arcrad_qarc)]
cavr += [rs.rect(lcav3,rm_width,cav_x4r,cav_y4r)]

cav_x5r, cav_y5r = [coords(cav_x4r,lcav3),coords(cav_y4r,arcrad+rm_width)]
cavr += [rs.halfarc(arcrad,rm_width,cav_x5r,cav_y5r,npoints=40, orientation='E')]

cav_x6r,cav_y6r = [coords(cav_x5r),coords(cav_y5r,arcrad)]
cavr += [rs.rect(-lcav3,rm_width,cav_x6r,cav_y6r)]

cav_x7r, cav_y7r = [coords(cav_x6r,-lcav3),coords(cav_y6r,arcrad_qarc+rm_width)]
cavr += [rs.quarterarc(arcrad_qarc,rm_width,cav_x7r,cav_y7r,npoints=40, orientation='SW')]

cav_x8r,cav_y8r = [coords(cav_x7r,-arcrad_qarc-rm_width),coords(cav_y7r)]
cavr += [rs.rect(rm_width,lcav2,cav_x8r,cav_y8r)]

cav_x9r, cav_y9r = [coords(cav_x8r,arcrad+rm_width),coords(cav_y8r,lcav2)]
cavr += [rs.halfarc(arcrad,rm_width,cav_x9r,cav_y9r,npoints=40, orientation='N')]

cav_x10r,cav_y10r = [coords(cav_x9r,arcrad),coords(cav_y9r)]
cavr += [rs.rect(rm_width,-lcav1,cav_x10r,cav_y10r)]

for i in range(0,len(cavr)):
	cavityr = gdspy.Polygon(cavr[i],3)
	# conductor = gdspy.fast_boolean(conductor,cavity, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(cavityr)

# Bragg Mirror Sections [layer 2]
###########################################################################
no_periods = 4
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

[make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 0]
[make_highZ(x) for x in range(len(arr_l)) if x % 2 == 1]

# Make upper Bragg periods
xb_strtr = xb_strt
yb_strtr = cav_y10 - lcav1
# yb_strtr = cavend[1][0][1] - lcav1 - taper_length

make_lowZ = lambda i: lowZ.rotate_mirror2(xb_strtr + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strtr,w_remove=wc, g_remove=gc)

make_highZ = lambda i: highZ.rotate_mirror2(xb_strtr + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strtr,w_remove=wc, g_remove = gc)

[make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 0]
[make_highZ(x) for x in range(len(arr_l)) if x % 2 == 1]


# Feedline sections [layer 2]
#
#

# Lower feed sections 
#
l1, l2, l3, arc = highZ.section_lengths(wc,gc)
cc, ratio, bond_pad, rfeed = [2*ghigh, .5, 400, 100]
feedin_length, feedlink_length, feed_st_length = [100,685,1600]
# rstrt = rlow + 100
# rlow = 100

# Low Z feedline sections 
feedline_low = Trench(wlow,glow,poly_cell, layer=2)

xf0Low = xb_strtr + no_periods*(lowZ.mirror_width() + highZ.mirror_width())
yf0Low = yb_strt
feedline_low.straight_trench(l1,xf0Low,yf0Low,orient='V')

xf1Low,yf1Low = [coords(xf0Low,rlow+2*gc+wc),coords(yf0Low,l1)]
feedline_low.halfarc_trench(rlow,xf1Low, yf1Low,orient='N',npoints=40)

xf2Low,yf2Low = [coords(xf1Low,rlow),coords(yf1Low)]
feedline_low.straight_trench(-l2-l3/8,xf2Low,yf2Low,orient='V')

xf3Low,yf3Low = [coords(xf2Low,-2*rlow),coords(yf2Low,-l2-l3/8)]
feedline_low.quarterarc_trench(rlow*2,xf3Low, yf3Low,orient='SE',npoints=40)

xf4Low,yf4Low = [coords(xf3Low),coords(yf3Low,-2*rlow-2*glow-wlow)]
feedline_low.straight_trench(-7*l3/8,xf4Low,yf4Low,orient='H')

# High Z feedline sections
feedline_high = Trench(whigh,ghigh,poly_cell, layer=2)

xf0High,yf0High = [coords(xf4Low,-7*l3/8),coords(yf4Low)]
feedline_high.straight_trench(-l1,xf0High,yf0High,orient='H')

xf1High,yf1High = [coords(xf0High,-l1),coords(yf0High,-rhigh)]
feedline_high.halfarc_trench(rhigh,xf1High, yf1High,orient='W',npoints=40)

xf2High,yf2High = [coords(xf1High),coords(yf1High,-rhigh-2*ghigh-whigh)]
feedline_high.straight_trench(l2,xf2High,yf2High,orient='H')

xf3High,yf3High = [coords(xf2High,l2),coords(yf2High,-rhigh)]
feedline_high.halfarc_trench(rhigh,xf3High, yf3High,orient='E',npoints=40)

xf4High,yf4High = [coords(xf3High),coords(yf3High,-rhigh-2*ghigh-whigh)]
feedline_high.straight_trench(-l3,xf4High,yf4High,orient='H')

xf5High,yf5High = [coords(xf4High,-l3),coords(yf4High,-2*rhigh)]
feedline_high.quarterarc_trench(2*rlow,xf5High,yf5High,orient='NW',npoints=20)

xf6High,yf6High = [coords(xf5High,-2*rhigh-2*ghigh-whigh),coords(yf5High)]
feedline_high.straight_trench(-300,xf6High,yf6High,orient='V')


bondl = 150
bondw = 4*bondl

xbond = xf6High - bondw/2 + ghigh + whigh/2
ybond = yf6High - 300 - bondl - 600

x0 = xf6High
y0 = yf6High - 300

x02 = x0 + ghigh + whigh

x1 = xbond
y1 = ybond + bondl

x2 = xbond + bondw - bondl
y2 = ybond + bondl + 300


feed = [rs.rect(bondw,bondl, xbond, ybond)]
feed += [rs.rect(bondl,300,xbond,ybond+bondl)]
feed += [rs.rect(bondl,300,xbond+bondw-bondl,ybond+bondl)]

d1 = [(x0, y0), (x0+ghigh, y0), (x1+bondl, y2), (x1, y2)]
d2 = [(x02, y0), (x02+ghigh, y0), (x1+bondw, y2), (x1+bondw-bondl, y2)]
feed += [d1,d2]

for i in range(0,len(feed)):
	outfeed = gdspy.Polygon(feed[i],2)
	# conductor = gdspy.fast_boolean(conductor,outfeed, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(outfeed)

# arcrad = .5*(2*rlow - glow - wlow)
arcrad_qarc = .5*(2*rqarc)

# Lower feed removes
x0_fdRem_L, y0_fdRem_L = [coords(xf0Low,-rm_width/2 + wlow/2 + glow),coords(yf0Low,l1)]
feedrL = [rs.rect(rm_width,-l1,x0_fdRem_L,y0_fdRem_L)]

x1_fdRem_L, y1_fdRem_L = [coords(x0_fdRem_L, arcrad+rm_width),coords(yf1Low)]
feedrL += [rs.halfarc(arcrad, rm_width, x1_fdRem_L, y1_fdRem_L, orientation='N', npoints=40)] 

x2_fdRem_L, y2_fdRem_L = [coords(x1_fdRem_L,arcrad),coords(y1_fdRem_L)]
feedrL += [rs.rect(rm_width, -l2-l3/8, x2_fdRem_L, y2_fdRem_L)]

x3_fdRem_L, y3_fdRem_L = [coords(x2_fdRem_L,-arcrad_qarc),coords(y2_fdRem_L-l2-l3/8)]
feedrL += [rs.quarterarc(arcrad_qarc, rm_width, x3_fdRem_L, y3_fdRem_L, 
	orientation='SE', npoints=40)] 

x4_fdRem_L, y4_fdRem_L = [coords(x3_fdRem_L),coords(y3_fdRem_L,-arcrad_qarc-rm_width)]
feedrL += [rs.rect(-7*l3/8 - l1, rm_width, x4_fdRem_L, y4_fdRem_L)]

x5_fdRem_L, y5_fdRem_L = [coords(x4_fdRem_L,-7*l3/8-l1),coords(y4_fdRem_L,-arcrad)]
feedrL += [rs.halfarc(arcrad, rm_width, x5_fdRem_L, y5_fdRem_L, 
	orientation='W', npoints=40)] 

x6_fdRem_L, y6_fdRem_L = [coords(x5_fdRem_L),coords(y5_fdRem_L,-arcrad-rm_width)]
feedrL += [rs.rect(l2,rm_width,x6_fdRem_L,y6_fdRem_L)]

x7_fdRem_L, y7_fdRem_L = [coords(x6_fdRem_L,l2),coords(y6_fdRem_L,-arcrad)]
feedrL += [rs.halfarc(arcrad, rm_width, x7_fdRem_L, y7_fdRem_L, 
	orientation='E', npoints=40)] 

x8_fdRem_L, y8_fdRem_L = [coords(x7_fdRem_L),coords(y7_fdRem_L,-arcrad-rm_width)]
feedrL += [rs.rect(-l3,rm_width,x8_fdRem_L,y8_fdRem_L)]

x9_fdRem_L, y9_fdRem_L = [coords(x8_fdRem_L,-l3+5),coords(y8_fdRem_L,-arcrad_qarc)]
feedrL += [rs.quarterarc(arcrad_qarc, rm_width, x9_fdRem_L, y9_fdRem_L, 
	orientation='NW', npoints=40)] 

x10_fdRem_L, y10_fdRem_L = [coords(x9_fdRem_L,-arcrad_qarc-rm_width),coords(y9_fdRem_L)]
feedrL += [rs.rect(rm_width,-300,x10_fdRem_L,y10_fdRem_L)]

for i in range(0,len(feedrL)):
	feedr = gdspy.Polygon(feedrL[i],3)
	# conductor = gdspy.fast_boolean(conductor,outfeed, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(feedr)

# Lower Feedbond Remove
bondlr = 180
bondwr = 4*bondl

xbond = xf6High - bondwr/2 + ghigh + whigh/2
ybond = yf6High - 300 - bondlr - 630

x0 = xf6High
y0 = yf6High - 300

x02 = x0 + ghigh + whigh

x1 = xbond
y1 = ybond + bondl

x2 = xbond + bondwr - bondlr
y2 = ybond + bondlr + 300

fbondr = [rs.rect(bondwr,bondwr-bondlr, xbond, ybond)]

trix0 = (x0 + ghigh + whigh/2) - rm_width/2
triy1 = ybond + bondwr-bondlr

d1 = [(trix0, y0), (trix0+rm_width, y0), (x1+bondwr, triy1), (x1, triy1)]
fbondr += [d1]

for i in range(0,len(fbondr)):
	feedbond_remove = gdspy.Polygon(fbondr[i],3)
	# conductor = gdspy.fast_boolean(conductor,outfeed, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(feedbond_remove)

# Upper feedline sections
#

# Low Z feedline sections
feedline_low = Trench(wlow,glow,poly_cell, layer=2)

xf0Low= xb_strtr + no_periods*(lowZ.mirror_width() + highZ.mirror_width())
yf0Low = yb_strtr
feedline_low.straight_trench(-l1,xf0Low,yf0Low,orient='V')

xf1Low,yf1Low = [coords(xf0Low,rlow+2*gc+wc),coords(yf0Low,-l1)]
feedline_low.halfarc_trench(rlow,xf1Low, yf1Low,orient='S',npoints=40)

xf2Low,yf2Low = [coords(xf1Low,rlow),coords(yf1Low)]
feedline_low.straight_trench(l2+l3/8,xf2Low,yf2Low,orient='V')

xf3Low,yf3Low = [coords(xf2Low,-2*rlow),coords(yf2Low,l2+l3/8)]
feedline_low.quarterarc_trench(2*rlow,xf3Low, yf3Low,orient='NE',npoints=40)

xf4Low,yf4Low = [coords(xf3Low),coords(yf3Low,2*rlow)]
feedline_low.straight_trench(-7*l3/8,xf4Low,yf4Low,orient='H')

# High Z feedline sections
feedline_high = Trench(whigh,ghigh,poly_cell, layer=2)

xf0High,yf0High = [coords(xf4Low,-7*l3/8),coords(yf4Low)]
feedline_high.straight_trench(-l1,xf0High,yf0High,orient='H')

xf1High,yf1High = [coords(xf0High,-l1),coords(yf0High,rhigh+2*ghigh+whigh)]
feedline_high.halfarc_trench(rhigh,xf1High, yf1High,orient='W',npoints=40)

xf2High,yf2High = [coords(xf1High),coords(yf1High,rhigh)]
feedline_high.straight_trench(l2,xf2High,yf2High,orient='H')

xf3High,yf3High = [coords(xf2High,l2),coords(yf2High,rhigh+2*ghigh+whigh)]
feedline_high.halfarc_trench(rhigh,xf3High, yf3High,orient='E',npoints=40)

xf4High,yf4High = [coords(xf3High),coords(yf3High,rhigh)]
feedline_high.straight_trench(-l3,xf4High,yf4High,orient='H')

xf5High,yf5High = [coords(xf4High,-l3),coords(yf4High,2*rhigh+2*ghigh+whigh)]
feedline_high.quarterarc_trench(2*rlow,xf5High,yf5High,orient='SW',npoints=20)

xf6High,yf6High = [coords(xf5High,-2*rhigh-2*ghigh-whigh),coords(yf5High)]
feedline_high.straight_trench(300,xf6High,yf6High,orient='V')


# bondl = 150
# bondw = 4*bondl

xbond = xf6High - bondw/2 + ghigh + whigh/2
ybond = yf6High + 300 + bondl + 600

x0 = xf6High
y0 = yf6High + 300

x02 = x0 + ghigh + whigh

x1 = xbond
y1 = ybond - 2*bondl

x2 = xbond + bondw - bondl
y2 = ybond - 2*bondl 


feed = [rs.rect(bondw,bondl, xbond, ybond)]
feed += [rs.rect(bondl,300,xbond,ybond-2*bondl)]
feed += [rs.rect(bondl,300,xbond+bondw-bondl,ybond-2*bondl)]

d1 = [(x0, y0), (x0+ghigh, y0), (x1+bondl, y2), (x1, y2)]
d2 = [(x02, y0), (x02+ghigh, y0), (x1+bondw, y2), (x1+bondw-bondl, y2)]
feed += [d1,d2]

for i in range(0,len(feed)):
	outfeed = gdspy.Polygon(feed[i],2)
	# conductor = gdspy.fast_boolean(conductor,outfeed, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(outfeed)



# Upper feed removes
x0_fdRem_U, y0_fdRem_U = [coords(xf0Low,-rm_width/2 + wlow/2 + glow),coords(yf0Low,-l1)]
feedrU = [rs.rect(rm_width,l1,x0_fdRem_U,y0_fdRem_U)]

x1_fdRem_U, y1_fdRem_U = [coords(x0_fdRem_U, arcrad+rm_width),coords(yf1Low)]
feedrU += [rs.halfarc(arcrad, rm_width, x1_fdRem_U, y1_fdRem_U, orientation='S', npoints=40)] 

x2_fdRem_U, y2_fdRem_U = [coords(x1_fdRem_U,arcrad),coords(y1_fdRem_U)]
feedrU += [rs.rect(rm_width, l2+l3/8, x2_fdRem_U, y2_fdRem_U)]

x3_fdRem_U, y3_fdRem_U = [coords(x2_fdRem_U,-arcrad_qarc),coords(y2_fdRem_U+l2+l3/8)]
feedrU += [rs.quarterarc(arcrad_qarc, rm_width, x3_fdRem_U, y3_fdRem_U, 
	orientation='NE', npoints=40)] 

x4_fdRem_U, y4_fdRem_U = [coords(x3_fdRem_U),coords(y3_fdRem_U,arcrad_qarc)]
feedrU += [rs.rect(-7*l3/8 - l1, rm_width, x4_fdRem_U, y4_fdRem_U)]

x5_fdRem_U, y5_fdRem_U = [coords(x4_fdRem_U,-7*l3/8-l1),coords(y4_fdRem_U,arcrad+rm_width)]
feedrU += [rs.halfarc(arcrad, rm_width, x5_fdRem_U, y5_fdRem_U, 
	orientation='W', npoints=40)] 

x6_fdRem_U, y6_fdRem_U = [coords(x5_fdRem_U),coords(y5_fdRem_U,arcrad)]
feedrU += [rs.rect(l2,rm_width,x6_fdRem_U,y6_fdRem_U)]

x7_fdRem_U, y7_fdRem_U = [coords(x6_fdRem_U,l2),coords(y6_fdRem_U,arcrad+rm_width)]
feedrU += [rs.halfarc(arcrad, rm_width, x7_fdRem_U, y7_fdRem_U, 
	orientation='E', npoints=40)] 

x8_fdRem_U, y8_fdRem_U = [coords(x7_fdRem_U),coords(y7_fdRem_U,arcrad)]
feedrU += [rs.rect(-l3,rm_width,x8_fdRem_U,y8_fdRem_U)]

x9_fdRem_U, y9_fdRem_U = [coords(x8_fdRem_U,-l3+5),coords(y8_fdRem_U,arcrad_qarc+rm_width)]
feedrU += [rs.quarterarc(arcrad_qarc, rm_width, x9_fdRem_U, y9_fdRem_U, 
	orientation='SW', npoints=40)] 

x10_fdRem_U, y10_fdRem_U = [coords(x9_fdRem_U,-arcrad_qarc-rm_width),coords(y9_fdRem_U)]
feedrU += [rs.rect(rm_width,300,x10_fdRem_U,y10_fdRem_U)]

for i in range(0,len(feedrU)):
	feedr = gdspy.Polygon(feedrU[i],3)
	# conductor = gdspy.fast_boolean(conductor,outfeed, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(feedr)


# Upper Feedbond Remove
bondlr = 180
bondwr = 4*bondl

xbond = xf6High - bondwr/2 + ghigh + whigh/2
# ybond = yf6High + 300 + bondlr + 630
ybond = yf6High + 300 + bondlr + 630 - 180

x0 = xf6High
y0 = yf6High + 300

x02 = x0 + ghigh + whigh

x1 = xbond
y1 = ybond + bondl

x2 = xbond + bondwr - bondlr
y2 = ybond + bondlr + 300

fbondr = [rs.rect(bondwr,bondwr-bondlr, xbond, ybond)]

# trix0 = (x0 + ghigh + whigh/2) - rm_width/2
# triy1 = ybond + bondwr-bondlr

# d1 = [(trix0, y0), (trix0+rm_width, y0), (x1+bondwr, triy1), (x1, triy1)]
# fbondr += [d1]

for i in range(0,len(fbondr)):
	feedbond_remove = gdspy.Polygon(fbondr[i],3)
	# conductor = gdspy.fast_boolean(conductor,outfeed, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(feedbond_remove)


###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
