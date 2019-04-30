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
xb_strt,yb_strt = [coords(725),coords(sub_y/2)- lext2 - lext3 - 140]
# lcav1, lcav2, lcav3 = [1000, 5500, 1000]
lcav1, lcav2, lcav3 = [600, 677.25, 2400]
lcav1, lcav2, lcav3 = [377.5, 1100, 2060.5]
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
print(l1+l2+l3+2*arc)
cc, ratio, bond_pad, rfeed = [2*ghigh, .5, 400, 100]
feedin_length, feedlink_length, feed_st_length = [100,685,1600]
rstrt = rlow + 100
rlow = 100

# Low Z feedline sections 
feedline_low = Trench(wlow,glow,poly_cell, layer=2)

xf0Low = xb_strtr + no_periods*(lowZ.mirror_width() + highZ.mirror_width())
yf0Low = yb_strt
feedline_low.straight_trench(l1,xf0Low,yf0Low,orient='V')

xf1Low,yf1Low = [coords(xf0Low,rstrt+2*gc+wc),coords(yf0Low,l1)]
feedline_low.halfarc_trench(rstrt,xf1Low, yf1Low,orient='N',npoints=40)

xf2Low,yf2Low = [coords(xf1Low,rstrt),coords(yf1Low)]
feedline_low.straight_trench(-l2,xf2Low,yf2Low,orient='V')

xf3Low,yf3Low = [coords(xf2Low),coords(yf2Low,-l2)]
feedline_low.straight_trench(-l3/4,xf3Low,yf3Low,orient='V')

xf4Low,yf4Low = [coords(xf3Low,-rlow),coords(yf3Low,-l3/4)]
feedline_low.quarterarc_trench(rlow,xf4Low,yf4Low,orient='SE',npoints=20)

xf5Low,yf5Low = [coords(xf4Low,-3*l3/4-arc/2+230),coords(yf4Low,-2*glow - wlow - rlow)]
feedline_low.straight_trench(3*l3/4+arc/2-230,xf5Low,yf5Low,orient='H')
# High Z feedline sections
feedline_high = Trench(whigh,ghigh,poly_cell, layer=2)

xf0High,yf0High = [coords(xf5Low,-l2-733/2),coords(yf5Low)]
feedline_high.straight_trench(l2+733/2,xf0High,yf0High,orient='H')

xf1High,yf1High = [coords(xf0High),coords(yf0High,-rhigh)]
feedline_high.halfarc_trench(rhigh,xf1High, yf1High,orient='W',npoints=40)

xf2High,yf2High = [coords(xf1High),coords(yf1High,-rhigh - 2*ghigh - whigh)]
feedline_high.straight_trench(l3+l1-733/2,xf2High,yf2High,orient='H')

xf3High,yf3High = [coords(xf2High,l3+l1-733/2),coords(yf2High,-rhigh)]
feedline_high.quarterarc_trench(rhigh,xf3High,yf3High,orient='NE',npoints=20)

xf4High,yf4High = [coords(xf3High,rhigh),coords(yf3High,-arc/2)]
feedline_high.straight_trench(arc/2,xf4High,yf4High,orient='V')

# Lower feedbond
xf5High,yf5High = [coords(xf4High,-2*whigh-4*ghigh),coords(yf4High-arc/2)]
feed_lower = LayoutComponents(poly_cell, xf5High,yf5High, width=whigh, gap=ghigh, layer=2)
feedbond = feed_lower.make_feedbond(arc/2,cc, ratio, bond_pad, 
	xf4High, yf4High, orientation='N')





# # Lower feed removes
# x0_fdRem_L, y0_fdRem_L = [coords(xf0Low,-rm_width/2 + wlow/2 + glow),coords(yf0Low,l1)]
# feed_remove_L = BuildRect(poly_cell,rm_width, -l1, layer = 3)
# feed_remove_L.make(x0_fdRem_L,y0_fdRem_L,layer=3)

# rad_feed = abs(.5*(x0_fdRem_L - (xf2Low + .5*(whigh + 2*ghigh) + rm_width/2)))

# x1_fdRem_L, y1_fdRem_L = [coords(x0_fdRem_L + rad_feed),coords(yf1Low)]
# rs.make_halfarc(-rad_feed, rm_width, x1_fdRem_L, y1_fdRem_L, 
# 	orientation='S', npoints=40, layer=3) 

# x2_fdRem_L, y2_fdRem_L = [coords(x1_fdRem_L,rad_feed-rm_width),coords(y1_fdRem_L)]
# feed_remove_L = BuildRect(poly_cell,rm_width, -l2-l3/4, layer = 3)
# feed_remove_L.make(x2_fdRem_L,y2_fdRem_L,layer=3)

# rqarc = x2_fdRem_L+rm_width-xf4Low

# x3_fdRem_L, y3_fdRem_L = [coords(x2_fdRem_L-rqarc+rm_width),coords(y2_fdRem_L,-l2-l3/4)]
# rs.make_quarterarc(rqarc, -rm_width, x3_fdRem_L, y3_fdRem_L, 
# 	orientation='SE', npoints=20, layer=3) 

# x4_fdRem_L, y4_fdRem_L = [coords(x3_fdRem_L),coords(y3_fdRem_L,-rqarc)]
# feed_remove_L = BuildRect(poly_cell,-3*l3/4-arc/2+230-l2-733/2,rm_width, layer = 3)
# feed_remove_L.make(x4_fdRem_L,y4_fdRem_L,layer=3)

# rharc = abs(.5*(y4_fdRem_L - (yf2High + .5*(whigh + 2*ghigh) + rm_width/2)))
# x5_fdRem_L, y5_fdRem_L = [coords(x4_fdRem_L,-3*l3/4-arc/2+230-l2-733/2),coords(y4_fdRem_L,-rharc)]
# rs.make_halfarc(rharc, rm_width, x5_fdRem_L, y5_fdRem_L, 
# 	orientation='W', npoints=40, layer=3) 

# x6_fdRem_L, y6_fdRem_L = [coords(x5_fdRem_L),coords(y5_fdRem_L,-rharc-rm_width)]
# feed_remove_L = BuildRect(poly_cell,l1+l3-733/2,rm_width, layer = 3)
# feed_remove_L.make(x6_fdRem_L,y6_fdRem_L,layer=3)

# x7_fdRem_L, y7_fdRem_L = [coords(x6_fdRem_L,l1+l3-733/2),coords(y6_fdRem_L)]
# rqarc2 = xf4High+rm_width-x7_fdRem_L-12
# rs.make_quarterarc(-rqarc2, rm_width, x7_fdRem_L, y7_fdRem_L-rqarc2+rm_width, 
# 	orientation='SW', npoints=20, layer=3) 

# x8_fdRem_L, y8_fdRem_L = [coords(x7_fdRem_L,rharc),coords(y7_fdRem_L,-arc/2-rharc)]
# feed_remove_L = BuildRect(poly_cell,rm_width, arc/2, layer = 3)
# feed_remove_L.make(x8_fdRem_L,y8_fdRem_L,layer=3)

# feed_remove = feed_lower.make_feedbond_remove(arc/2,cc, ratio, 
#         bond_pad, x8_fdRem_L,y8_fdRem_L,x8_fdRem_L,
#         y8_fdRem_L,x8_fdRem_L+rm_width, orientation='N')

# # Upper feedline sections
# #

# # Low Z feedline sections
# feedline_low = Trench(wlow,glow,poly_cell, layer=2)

# xf0Low= xb_strtr + no_periods*(lowZ.mirror_width() + highZ.mirror_width())
# yf0Low = yb_strtr
# feedline_low.straight_trench(-l1,xf0Low,yf0Low,orient='V')

# xf1Low,yf1Low = [coords(xf0Low,rstrt+2*gc+wc),coords(yf0Low,-l1)]
# feedline_low.halfarc_trench(rstrt,xf1Low, yf1Low,orient='S',npoints=40)

# xf2Low,yf2Low = [coords(xf1Low,rstrt),coords(yf1Low)]
# feedline_low.straight_trench(l2,xf2Low,yf2Low,orient='V')

# xf3Low,yf3Low = [coords(xf2Low),coords(yf2Low,l2)]
# feedline_low.straight_trench(l3/4,xf3Low,yf3Low,orient='V')

# xf4Low,yf4Low = [coords(xf3Low,-rlow),coords(yf3Low,l3/4)]
# feedline_low.quarterarc_trench(rlow,xf4Low,yf4Low,orient='NE',npoints=20)

# xf5Low,yf5Low = [coords(xf4Low,-3*l3/4-arc/2+230),coords(yf4Low,rlow)]
# feedline_low.straight_trench(3*l3/4+arc/2-230,xf5Low,yf5Low,orient='H')

# # High Z feedline sections
# xf0High,yf0High = [coords(xf5Low,-l2-733/2),coords(yf5Low)]
# feedline_high.straight_trench(l2+733/2,xf0High,yf0High,orient='H')

# xf1High,yf1High = [coords(xf0High),coords(yf0High,rhigh + 2*ghigh + whigh)]
# feedline_high.halfarc_trench(rhigh,xf1High, yf1High,orient='W',npoints=40)

# xf2High,yf2High = [coords(xf1High),coords(yf1High,rhigh )]
# feedline_high.straight_trench(l3+l1-733/2,xf2High,yf2High,orient='H')

# xf3High,yf3High = [coords(xf2High,l3+l1-733/2),coords(yf2High,rhigh + 2*ghigh + whigh)]
# feedline_high.quarterarc_trench(rhigh,xf3High,yf3High,orient='SE',npoints=20)

# xf4High,yf4High = [coords(xf3High,rhigh),coords(yf3High)]
# feedline_high.straight_trench(arc/2,xf4High,yf4High,orient='V')

# # Lower feedbond
# xf5High,yf5High = [coords(xf4High,-2*whigh-4*ghigh),coords(yf4High-arc/2)]
# feed_lower = LayoutComponents(poly_cell, xf5High,yf5High, width=whigh, gap=ghigh, layer=2)
# feedbond = feed_lower.make_feedbond(arc/2,cc, ratio, bond_pad, 
# 	xf4High, yf4High+arc/2, orientation='S')

# # Lower feedbond removes
# #
# x0_fdRem_U, y0_fdRem_U = [coords(xf0Low,-rm_width/2 + wlow/2 + glow),coords(yf0Low,-l1)]
# feed_remove_U = BuildRect(poly_cell,rm_width, l1, layer = 3)
# feed_remove_U.make(x0_fdRem_U,y0_fdRem_U,layer=3)

# x1_fdRem_U, y1_fdRem_U = [coords(x0_fdRem_U + rad_feed),coords(yf1Low)]
# rs.make_halfarc(-rad_feed, rm_width, x1_fdRem_U, y1_fdRem_U, 
# 	orientation='N', npoints=40, layer=3) 

# x2_fdRem_U, y2_fdRem_U = [coords(x1_fdRem_U,rad_feed-rm_width),coords(y1_fdRem_U)]
# feed_remove_U = BuildRect(poly_cell,rm_width, l2+l3/4, layer = 3)
# feed_remove_U.make(x2_fdRem_U,y2_fdRem_U,layer=3)

# x3_fdRem_U, y3_fdRem_U = [coords(x2_fdRem_U-rqarc+rm_width),coords(y2_fdRem_U,l2+l3/4)]
# rs.make_quarterarc(rqarc, -rm_width, x3_fdRem_U, y3_fdRem_U, 
# 	orientation='NE', npoints=20, layer=3) 

# x4_fdRem_U, y4_fdRem_U = [coords(x3_fdRem_U),coords(y3_fdRem_U,rqarc-rm_width)]
# feed_remove_U = BuildRect(poly_cell,-3*l3/4-arc/2+230-l2-733/2,rm_width, layer = 3)
# feed_remove_U.make(x4_fdRem_U,y4_fdRem_U,layer=3)

# x5_fdRem_U, y5_fdRem_U = [coords(x4_fdRem_U,-3*l3/4-arc/2+230-l2-733/2),coords(y4_fdRem_U,rharc+rm_width)]
# rs.make_halfarc(rharc, rm_width, x5_fdRem_U, y5_fdRem_U, 
# 	orientation='W', npoints=40, layer=3) 

# x6_fdRem_U, y6_fdRem_U = [coords(x5_fdRem_U),coords(y5_fdRem_U,rharc)]
# feed_remove_U = BuildRect(poly_cell,l1+l3-733/2,rm_width, layer = 3)
# feed_remove_U.make(x6_fdRem_U,y6_fdRem_U,layer=3)

# x7_fdRem_U, y7_fdRem_U = [coords(x6_fdRem_U,l1+l3-733/2),coords(y6_fdRem_U)]
# rs.make_quarterarc(-rqarc2, rm_width, x7_fdRem_U, y7_fdRem_U+rqarc2, 
# 	orientation='NW', npoints=20, layer=3) 

# x8_fdRem_U, y8_fdRem_U = [coords(x7_fdRem_U,rharc),coords(y7_fdRem_U,rqarc2)]
# feed_remove_U = BuildRect(poly_cell,rm_width, arc/2, layer = 3)
# feed_remove_U.make(x8_fdRem_U,y8_fdRem_U,layer=3)

# feed_remove = feed_lower.make_feedbond_remove(arc/2,cc, ratio, 
#         bond_pad, x8_fdRem_U,y8_fdRem_U+100,x8_fdRem_U,
#         y8_fdRem_U+arc/2,x8_fdRem_U+rm_width, orientation='S')

###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
