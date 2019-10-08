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
layout_file ='fab_files/ShortCavityBragg2_HL_7p2G.gds'

# Parameters
#__________________________________________________________
sub_x, sub_y = [4000, 9000] # substrate dimensions
wc, gc, lc = [8.11, 17.85, 8108.45] # Cavity width, gap, length
wlow, llow = [30.44, 4051.32]  # Low Z section
whigh, lhigh = [2, 4051.32] # High Z section
glow, ghigh = [.5*(wc + 2*gc - wlow),.5*(wc + 2*gc - whigh)]

rext, rlow, rhigh = [0, 40, 40] # radii

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
xb_strt,yb_strt = [coords(1000),coords(sub_y/2)- lext2 - lext3 - 140]
lcav1, lcav2, lcav3 = [1000, 5500, 1000]
taper_length = 100

cavity = Trench(wc, gc, poly_cell, layer = 2)


lcavity = 8108
rcav = 100
no_periods = 4
cav_mirror = bragg.Bragg(wlow, glow, llow, poly_cell, radius=rlow, layer=2)
lcav3p = 2*no_periods*cav_mirror.mirror_width()
a1 = 3*np.pi*rlow 
a2 = np.pi*rcav
ls = (lcavity - a1 - a2 - 2*lcav3p - 2*taper_length)/2

print(2*ls + 2*lcav3p + a1 + a2 + 2*taper_length)

cav_x0,cav_y0 = [coords(xb_strt),coords(yb_strt,-ls/2)]
strait = cavity.straight_trench(ls/2-taper_length, cav_x0, cav_y0, orient='V')

cav_xtaper, cav_ytaper = [coords(xb_strt),coords(yb_strt,-taper_length)]
cavity.taper(wc, gc, wlow, glow, cav_x0, 
        cav_y0+ls/2-taper_length, cav_x0, cav_y0+ls/2)

cav_x1,cav_y1 = [coords(xb_strt,-rlow),coords(yb_strt,-ls/2)]
cavity.halfarc_trench(rlow,cav_x1,cav_y1,orient='S',npoints=40)

cav_x2,cav_y2 = [coords(xb_strt,-2*rlow-wlow-2*glow),coords(yb_strt,-ls/2)]
cavity.straight_trench(lcav2/3,cav_x2,cav_y2,orient='V')

cav_x2q,cav_y2q = [coords(cav_x2,rcav+2*gc+wc),coords(cav_y2,lcav2/3)]
cavity.quarterarc_trench(rcav,cav_x2q,cav_y2q,orient='NW',npoints=40)

cav_x2s,cav_y2s = [coords(cav_x2q),coords(cav_y2q,rcav)]
cavity.straight_trench(lcav3p,cav_x2s,cav_y2s,orient='H')

cav_x2h,cav_y2h = [coords(cav_x2s,lcav3p),coords(cav_y2s,rlow+2*gc+wc)]
cavity.halfarc_trench(rlow,cav_x2h,cav_y2h,orient='E',npoints=40)

cav_x2s2,cav_y2s2 = [coords(cav_x2h),coords(cav_y2h,rlow)]
cavity.straight_trench(-lcav3p,cav_x2s2,cav_y2s2,orient='H')

cav_x2q2,cav_y2q2 = [coords(cav_x2s2,-lcav3p),coords(cav_y2s2,rcav+2*gc+wc)]
cavity.quarterarc_trench(rcav,cav_x2q2,cav_y2q2,orient='SW',npoints=40)

cav_x2s3,cav_y2s3 = [coords(cav_x2q2,-rcav-2*gc-wc),coords(cav_y2q2)]
cavity.straight_trench(lcav3p,cav_x2s3,cav_y2s3,orient='V')

cav_x3,cav_y3 = [coords(cav_x2s3,rlow+2*gc+wc),coords(cav_y2s3,lcav2/3)]
cavity.halfarc_trench(rlow,cav_x3,cav_y3,orient='N',npoints=40)

cav_x4,cav_y4 = [coords(cav_x3,2*gc+wc),coords(cav_y3,-lcav3+taper_length)]
cavend = cavity.straight_trench(lcav3-taper_length,cav_x4,cav_y4,orient='V')

cavity.taper(wlow, glow, wc, gc, cav_x4, 
       cav_y4-taper_length, cav_x4, cav_y4)

# Cavity removes [layer 3]
############################################################################

# Cavity Removes
rm_width = 4*wc + 2*gc
arcrad = .5*(2*rlow - gc - wc)

# Lower cevity extrude straight remove
cav_x0r, cav_y0r = [coords(cav_x0,-rm_width/2+wc/2+gc),coords(cav_y0)]
cavity_remove = BuildRect(poly_cell,rm_width, lcav1, layer = 3)
straight_remove_L = cavity_remove.make(cav_x0r,cav_y0r,layer=3)

# Centre cavity straight remove
#cav_x1r, cav_y1r = [coords(cav_x0,-2*rlow-wlow-2*glow-rm_width/2),coords(yb_strt,-lcav1)]
cav_x1r, cav_y1r = [coords(cav_x2,-rm_width/2 + gc + wc/2),coords(yb_strt,-lcav1)]
cavity_remove = BuildRect(poly_cell,rm_width, lcav2, layer = 3)
straight_remove_C = cavity_remove.make(cav_x1r,cav_y1r,layer=3)

# Upper cavity straight remove
cav_x2r, cav_y2r = [coords(cav_x4,-rm_width/2 + wc/2+gc),coords(cav_y4)]
cavity_remove = BuildRect(poly_cell,rm_width, lcav3, layer = 3)
straight_remove_U = cavity_remove.make(cav_x2r,cav_y2r-taper_length,layer=3)

# Lower cavity halfarc remove
rad = (cav_x0r - (cav_x1r + rm_width))/2
cav_xhfrL, cav_yhfrL = [coords(cav_x0r, - rad),coords(cav_y1)]
cav_harc_remove = rs.make_halfarc(rad, rm_width,
	cav_xhfrL, cav_yhfrL, orientation='S', npoints=40, layer=3) 

# Upper cavity halfarc remove
cav_xhfrU, cav_yhfrU = [coords(cav_x0r, - rad),coords(cav_y1,lcav2)]
cav_harc_remove = rs.make_halfarc(rad, rm_width,
	cav_xhfrU, cav_yhfrU, orientation='N', npoints=40, layer=3) 

# Bragg Mirror Sections [layer 2]
###########################################################################

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
yb_strtr = cavend[1][0][1] - taper_length

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
rstrt = rlow #+ 70
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

lf = -3*l3/4-arc/2+230-373
lfm = 3*l3/4+arc/2-230+373
xf5Low,yf5Low = [coords(xf4Low,lf),coords(yf4Low,-2*glow - wlow - rlow)]
feedline_low.straight_trench(lfm,xf5Low,yf5Low,orient='H')

# High Z feedline sections
feedline_high = Trench(whigh,ghigh,poly_cell, layer=2)

hs1 = -l2-733/2+373/2
hs1m = l2+733/2-373/2
xf0High,yf0High = [coords(xf5Low,hs1/2+42),coords(yf5Low)]
feedline_high.straight_trench(hs1m/2-42,xf0High,yf0High,orient='H')

xf1High,yf1High = [coords(xf0High),coords(yf0High,-rhigh)]
feedline_high.halfarc_trench(rhigh,xf1High, yf1High,orient='W',npoints=40)

lf2 = l3+l1-733/2-hs1/2+373/2
lf = 1680+42+452/2
lfp = 1000-452/2

xf2High,yf2High = [coords(xf1High),coords(yf1High,-rhigh - 2*ghigh - whigh)]
feedline_high.straight_trench(lf,xf2High,yf2High,orient='H')

xf2pHigh,yf2pHigh = [coords(xf1High,lf),coords(yf1High,-2*rhigh-2*ghigh-whigh)]
feedline_high.halfarc_trench(rhigh,xf2pHigh, yf2pHigh,orient='E',npoints=40)

xf2ppHigh,yf2ppHigh = [coords(xf2pHigh,-lfp),coords(yf2pHigh,-rhigh-2*ghigh-whigh)]
feedline_high.straight_trench(lfp,xf2ppHigh,yf2ppHigh,orient='H')

xf3High,yf3High = [coords(xf2ppHigh),coords(yf2ppHigh,-rhigh)]
feedline_high.quarterarc_trench(rhigh,xf3High,yf3High,orient='NW',npoints=20)

xf4High,yf4High = [coords(xf3High,-rhigh-2*ghigh-whigh),coords(yf3High,-arc/2)]
feedline_high.straight_trench(arc/2,xf4High,yf4High,orient='V')

# Lower feedbond
xf5High,yf5High = [coords(xf4High,-2*whigh-4*ghigh),coords(yf4High-arc/2)]
feed_lower = LayoutComponents(poly_cell, xf5High,yf5High, width=whigh, gap=ghigh, layer=2)
feedbond = feed_lower.make_feedbond(arc/2,cc, ratio, bond_pad, 
	xf4High, yf4High, orientation='N')

# Lower feed removes
x0_fdRem_L, y0_fdRem_L = [coords(xf0Low,-rm_width/2 + wlow/2 + glow),coords(yf0Low,l1)]
feed_remove_L = BuildRect(poly_cell,rm_width, -l1, layer = 3)
feed_remove_L.make(x0_fdRem_L,y0_fdRem_L,layer=3)

rad_feed = abs(.5*(x0_fdRem_L - (xf2Low + .5*(whigh + 2*ghigh) + rm_width/2)))

x1_fdRem_L, y1_fdRem_L = [coords(x0_fdRem_L + rad_feed),coords(yf1Low)]
rs.make_halfarc(-rad_feed, rm_width, x1_fdRem_L, y1_fdRem_L, 
	orientation='S', npoints=40, layer=3) 

x2_fdRem_L, y2_fdRem_L = [coords(x1_fdRem_L,rad_feed-rm_width),coords(y1_fdRem_L)]
feed_remove_L = BuildRect(poly_cell,rm_width, -l2-l3/4, layer = 3)
feed_remove_L.make(x2_fdRem_L,y2_fdRem_L,layer=3)

rqarc = x2_fdRem_L+rm_width-xf4Low

x3_fdRem_L, y3_fdRem_L = [coords(x2_fdRem_L-rqarc+rm_width),coords(y2_fdRem_L,-l2-l3/4)]
rs.make_quarterarc(rqarc, -rm_width, x3_fdRem_L, y3_fdRem_L, 
	orientation='SE', npoints=20, layer=3) 

x4_fdRem_L, y4_fdRem_L = [coords(x3_fdRem_L,-lfm+hs1/2+42),coords(y3_fdRem_L,-rqarc)]
feed_remove_L = BuildRect(poly_cell,lfm-hs1/2-42,rm_width, layer = 3)
feed_remove_L.make(x4_fdRem_L,y4_fdRem_L,layer=3)

rharc = abs(.5*(y4_fdRem_L - (yf2High + .5*(whigh + 2*ghigh) + rm_width/2)))
x5_fdRem_L, y5_fdRem_L = [coords(x4_fdRem_L),coords(y4_fdRem_L,-rharc)]
rs.make_halfarc(rharc, rm_width, x5_fdRem_L, y5_fdRem_L, 
	orientation='W', npoints=40, layer=3) 

x6_fdRem_L, y6_fdRem_L = [coords(x5_fdRem_L),coords(y5_fdRem_L,-rharc-rm_width)]
feed_remove_L = BuildRect(poly_cell,lf,rm_width, layer = 3)
feed_remove_L.make(x6_fdRem_L,y6_fdRem_L,layer=3)

x6p_fdRem_L, y6p_fdRem_L = [coords(x5_fdRem_L,lf),coords(y5_fdRem_L,-2*rharc-rm_width)]
rs.make_halfarc(rharc, rm_width, x6p_fdRem_L, y6p_fdRem_L, 
	orientation='E', npoints=40, layer=3) 

x6pp_fdRem_L, y6pp_fdRem_L = [coords(x6p_fdRem_L,-lfp),coords(y6p_fdRem_L,-rharc-2*rm_width/2)]
feed_remove_L = BuildRect(poly_cell,lfp,rm_width, layer = 3)
feed_remove_L.make(x6pp_fdRem_L,y6pp_fdRem_L,layer=3)

x7_fdRem_L, y7_fdRem_L = [coords(x6pp_fdRem_L),coords(y6pp_fdRem_L,-2*rharc-rm_width)]
rqarc2 = xf4High+rm_width-x7_fdRem_L-12
rs.make_quarterarc(-rqarc2, rm_width, x7_fdRem_L, y7_fdRem_L-rqarc2+rm_width, 
	orientation='NW', npoints=20, layer=3) 

x8_fdRem_L, y8_fdRem_L = [coords(x7_fdRem_L,-rharc-rm_width),coords(y7_fdRem_L)]
feed_remove_L = BuildRect(poly_cell,rm_width, arc/2, layer = 3)
feed_remove_L.make(x8_fdRem_L,y8_fdRem_L,layer=3)

feed_remove = feed_lower.make_feedbond_remove(arc/2,cc, ratio, 
        bond_pad, x8_fdRem_L,y8_fdRem_L,x8_fdRem_L,
        y8_fdRem_L,x8_fdRem_L+rm_width, orientation='N')

# # Upper feedline sections
# #

# # Low Z feedline sections
xf0Low= xb_strtr + no_periods*(lowZ.mirror_width() + highZ.mirror_width())
yf0Low = yb_strtr
feedline_low.straight_trench(-l1,xf0Low,yf0Low,orient='V')

xf0Low= xb_strtr + no_periods*(lowZ.mirror_width() + highZ.mirror_width())
yf0Low = yb_strtr
feedline_low.straight_trench(-l1,xf0Low,yf0Low,orient='V')

xf1Low,yf1Low = [coords(xf0Low,rstrt+2*gc+wc),coords(yf0Low,-l1)]
feedline_low.halfarc_trench(rstrt,xf1Low, yf1Low,orient='S',npoints=40)

xf2Low,yf2Low = [coords(xf1Low,rstrt),coords(yf1Low)]
feedline_low.straight_trench(l2,xf2Low,yf2Low,orient='V')

xf3Low,yf3Low = [coords(xf2Low),coords(yf2Low,l2)]
feedline_low.straight_trench(l3/4,xf3Low,yf3Low,orient='V')

xf4Low,yf4Low = [coords(xf3Low,-rlow),coords(yf3Low,l3/4)]
feedline_low.quarterarc_trench(rlow,xf4Low,yf4Low,orient='NE',npoints=20)

xf5Low,yf5Low = [coords(xf4Low,-lfm),coords(yf4Low,rlow)]
feedline_low.straight_trench(lfm,xf5Low,yf5Low,orient='H')

# High Z feedline sections
feedline_high = Trench(whigh,ghigh,poly_cell, layer=2)

xf0High,yf0High = [coords(xf5Low,hs1/2+42),coords(yf5Low)]
feedline_high.straight_trench(hs1m/2-42,xf0High,yf0High,orient='H')

xf1High,yf1High = [coords(xf0High),coords(yf0High,rhigh+2*ghigh + whigh)]
feedline_high.halfarc_trench(rhigh,xf1High, yf1High,orient='W',npoints=40)

xf2High,yf2High = [coords(xf1High),coords(yf1High,rhigh)]
feedline_high.straight_trench(lf,xf2High,yf2High,orient='H')

xf2pHigh,yf2pHigh = [coords(xf1High,lf),coords(yf1High,2*rhigh+2*ghigh+whigh)]
feedline_high.halfarc_trench(rhigh,xf2pHigh, yf2pHigh,orient='E',npoints=40)

xf2ppHigh,yf2ppHigh = [coords(xf2pHigh,-lfp),coords(yf2pHigh,rhigh)]
feedline_high.straight_trench(lfp,xf2ppHigh,yf2ppHigh,orient='H')

xf3High,yf3High = [coords(xf2ppHigh),coords(yf2ppHigh,rhigh+2*ghigh+whigh)]
feedline_high.quarterarc_trench(rhigh,xf3High,yf3High,orient='SW',npoints=20)

xf4High,yf4High = [coords(xf3High,-rhigh-2*ghigh-whigh),coords(yf3High,arc/2)]
feedline_high.straight_trench(-arc/2,xf4High,yf4High,orient='V')

# Upper feedbond
xf5High,yf5High = [coords(xf4High,-2*whigh-4*ghigh),coords(yf4High,-arc/2)]
feed_lower = LayoutComponents(poly_cell, xf5High,yf5High, width=whigh, gap=ghigh, layer=2)
feedbond = feed_lower.make_feedbond(arc/2,cc, ratio, bond_pad, 
	xf4High, yf4High, orientation='S')

# Upper feed removes
x0_fdRem_L, y0_fdRem_L = [coords(xf0Low,-rm_width/2 + wlow/2 + glow),coords(yf0Low,-l1)]
feed_remove_L = BuildRect(poly_cell,rm_width, l1, layer = 3)
feed_remove_L.make(x0_fdRem_L,y0_fdRem_L,layer=3)

x1_fdRem_L, y1_fdRem_L = [coords(x0_fdRem_L + rad_feed),coords(yf1Low)]
rs.make_halfarc(-rad_feed, rm_width, x1_fdRem_L, y1_fdRem_L, 
	orientation='N', npoints=40, layer=3)

x2_fdRem_L, y2_fdRem_L = [coords(x1_fdRem_L,rad_feed-rm_width),coords(y1_fdRem_L)]
feed_remove_L = BuildRect(poly_cell,rm_width, l2+l3/4, layer = 3)
feed_remove_L.make(x2_fdRem_L,y2_fdRem_L,layer=3)

x3_fdRem_L, y3_fdRem_L = [coords(x2_fdRem_L-rqarc+rm_width),coords(y2_fdRem_L,l2+l3/4)]
rs.make_quarterarc(rqarc, -rm_width, x3_fdRem_L, y3_fdRem_L, 
	orientation='NE', npoints=20, layer=3) 

x4_fdRem_L, y4_fdRem_L = [coords(x3_fdRem_L,-lfm+hs1/2+42),coords(y3_fdRem_L,rqarc-rm_width)]
feed_remove_L = BuildRect(poly_cell,lfm-hs1/2-42,rm_width, layer = 3)
feed_remove_L.make(x4_fdRem_L,y4_fdRem_L,layer=3)

x5_fdRem_L, y5_fdRem_L = [coords(x4_fdRem_L),coords(y4_fdRem_L,rharc+rm_width)]
rs.make_halfarc(rharc, rm_width, x5_fdRem_L, y5_fdRem_L, 
	orientation='W', npoints=40, layer=3) 

x6_fdRem_L, y6_fdRem_L = [coords(x5_fdRem_L),coords(y5_fdRem_L,rharc)]
feed_remove_L = BuildRect(poly_cell,lf,rm_width, layer = 3)
feed_remove_L.make(x6_fdRem_L,y6_fdRem_L,layer=3)

x6p_fdRem_L, y6p_fdRem_L = [coords(x5_fdRem_L,lf),coords(y5_fdRem_L,2*rharc+rm_width)]
rs.make_halfarc(rharc, rm_width, x6p_fdRem_L, y6p_fdRem_L, 
	orientation='E', npoints=40, layer=3) 

x6pp_fdRem_L, y6pp_fdRem_L = [coords(x6p_fdRem_L,-lfp),coords(y6p_fdRem_L,rharc)]
feed_remove_L = BuildRect(poly_cell,lfp,rm_width, layer = 3)
feed_remove_L.make(x6pp_fdRem_L,y6pp_fdRem_L,layer=3)

x7_fdRem_L, y7_fdRem_L = [coords(x6pp_fdRem_L),coords(y6pp_fdRem_L)]
rqarc2 = xf4High+rm_width-x7_fdRem_L-12
rs.make_quarterarc(-rqarc2, rm_width, x7_fdRem_L, y7_fdRem_L-rqarc2+rm_width, 
	orientation='SW', npoints=20, layer=3) 

x8_fdRem_L, y8_fdRem_L = [coords(x7_fdRem_L,-rharc-rm_width),coords(y7_fdRem_L,-rqarc2+rm_width+arc/2)]
feed_remove_L = BuildRect(poly_cell,rm_width, -arc/2, layer = 3)
feed_remove_L.make(x8_fdRem_L,y8_fdRem_L,layer=3)

feed_remove = feed_lower.make_feedbond_remove(arc/2,cc, ratio, 
        bond_pad, x8_fdRem_L,y8_fdRem_L,x8_fdRem_L,
        y8_fdRem_L,x8_fdRem_L+rm_width, orientation='S')

###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
