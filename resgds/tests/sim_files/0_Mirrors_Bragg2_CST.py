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
layout_file ='0_Mirrors_Bragg2_CST.gds'

# Parameters
#__________________________________________________________
sub_x, sub_y = [1700, 6000] # substrate dimensions
wc, gc, lc = [8.11, 17.85, 8108.45] # Cavity width, gap, length
wlow, llow = [30.44, 4051.32]  # Low Z section
whigh, lhigh = [2, 4051.32] # High Z section
glow, ghigh = [.5*(wc + 2*gc - wlow),.5*(wc + 2*gc - whigh)]

rext, rlow, rhigh = [0, 55, 55] # radii

lext1, lext2 = [400, 1200] # Extrude lengths
lext3 = llow - lext1 - lext2 - 500*np.pi - 150*np.pi

# Start making resonator geometry
############################################################################

# # Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# Substrate coordinate list
sub = rs.rect(sub_x,sub_y,0,0)
substrate = gdspy.Polygon(sub, layer=0)

# Cavity sections
#
coords = lambda x,dx=0: x+dx
# xb_strt,yb_strt = [coords(1250),coords(sub_y/2)- lext2 - lext3 - 140]
xb_strt,yb_strt = [755,1300]
lcav1, lcav2, lcav3 = [1000, 5500, 100]
taper_length = 100

cav_x0,cav_y0 = [coords(xb_strt,-rlow),coords(yb_strt,-lcav1-rlow-wc)] 
cav_cond = [rs.rect(lcav1, wc, cav_x0, cav_y0)]

cav_x1,cav_y1 = [coords(xb_strt,-rlow),coords(yb_strt,-lcav1)]
cav_cond += [rs.quarterarc(rlow,wc,cav_x1,cav_y1,orientation='SW',npoints=40)]

cav_x2,cav_y2 = [coords(xb_strt,-2*rlow-wc),coords(yb_strt,-lcav1)]
cav_cond += [rs.rect(wc,lcav2,cav_x2,cav_y2)]

cav_x3,cav_y3 = [coords(xb_strt,-rlow),coords(yb_strt,lcav2-lcav1)]
cav_cond += [rs.quarterarc(rlow,wc,cav_x3,cav_y3,orientation='NW',npoints=40)]

cav_x4,cav_y4 = [coords(xb_strt,-rlow),coords(cav_y3,rlow)]
cav_cond += [rs.rect(lcav1,wc,cav_x4,cav_y4)]


for i in range(0,len(cav_cond)):
	cavity = gdspy.Polygon(cav_cond[i],1)
	poly_cell.add(cavity)


# Cavity substrate remove
crmw = wc+2*gc

cav_x0r,cav_y0r = [coords(xb_strt,-gc),coords(yb_strt,-lcav1-rlow+gc-crmw)] 
cav_rm = [rs.rect(lcav1,crmw, cav_x0r-rlow+gc, cav_y0r)]

cav_x1r,cav_y1r = [coords(cav_x0r,-rlow+gc),coords(yb_strt,-lcav1)]
cav_rm += [rs.quarterarc(rlow-gc,crmw,cav_x1r,cav_y1r,orientation='SW',npoints=40)]

cav_x2r,cav_y2r = [coords(xb_strt,-2*rlow-gc-wc),coords(yb_strt,-lcav1)]
cav_rm += [rs.rect(crmw,lcav2,cav_x2r,cav_y2r)]

cav_x3r,cav_y3r = [coords(cav_x0r,-rlow+gc),coords(yb_strt,lcav2-lcav1)]
cav_rm += [rs.quarterarc(rlow-gc,crmw,cav_x3r,cav_y3r,orientation='NW',npoints=40)]

cav_x4r,cav_y4r = [coords(cav_x0r),coords(cav_y3r,rlow+gc+wc-crmw)]
cav_rm += [rs.rect(lcav1,crmw,cav_x0r-rlow+gc,cav_y4r)]

for i in range(0,len(cav_rm)):
	remove = gdspy.Polygon(cav_rm[i],2)
	substrate = gdspy.fast_boolean(substrate,remove, 'not', 
		precision=1e-9, max_points=1000, layer=0)


# # Bragg Mirror Sections
# ###########################################################################

# # LOWER BRAGG SECTIONS
# ######################
# no_periods = 4
# highZ = bragg.BraggCST(whigh, ghigh, lhigh, poly_cell, radius=rhigh, layer=2)
# lowZ = bragg.BraggCST(wlow, glow, llow, poly_cell, radius=rlow, layer=2)
# rmw = wc+2*gc
# rmlZ = bragg.BraggCST(rmw, gc, llow, poly_cell, radius=48.315, layer=2)
# rmhZ = bragg.BraggCST(rmw, gc, lhigh, poly_cell, radius=34.095, layer=2)

# xlz1,ylz1 = [coords(xb_strt+wc/2-wlow/2),coords(yb_strt)]
# lz = [lowZ.mirror(xlz1,ylz1, w_remove=wc, g_remove=gc)]

# xhz1,yhz1 = [coords(xlz1-wlow/2-whigh/2+lowZ.mirror_width()),coords(yb_strt)]
# hz = [highZ.mirror(xhz1,yhz1, w_remove=wc, g_remove=gc)]

# xlz2,ylz2 = [coords(xhz1-whigh/2-wlow/2+highZ.mirror_width()),coords(yb_strt)]
# lz += [lowZ.mirror(xlz2,ylz2, w_remove=wc, g_remove=gc)]

# xhz2,yhz2 = [coords(xlz2-wlow/2-whigh/2+lowZ.mirror_width()),coords(yb_strt)]
# hz += [highZ.mirror(xhz2,yhz2, w_remove=wc, g_remove=gc)]

# xlz3,ylz3 = [coords(xhz2-whigh/2-wlow/2+highZ.mirror_width()),coords(yb_strt)]
# lz += [lowZ.mirror(xlz3,ylz3, w_remove=wc, g_remove=gc)]

# xhz3,yhz3 = [coords(xlz3-wlow/2-whigh/2+lowZ.mirror_width()),coords(yb_strt)]
# hz += [highZ.mirror(xhz3,yhz3, w_remove=wc, g_remove=gc)]

# xlz4,ylz4 = [coords(xhz3-whigh/2-wlow/2+highZ.mirror_width()),coords(yb_strt)]
# lz += [lowZ.mirror(xlz4,ylz4, w_remove=wc, g_remove=gc)]

# xhz4,yhz4 = [coords(xlz4-wlow/2-whigh/2+lowZ.mirror_width()),coords(yb_strt)]
# hz += [highZ.mirror(xhz4,yhz4, w_remove=wc, g_remove=gc)]

# # LOWER BRAGG SECTION REMOVES
# #############################

# ll1,ll2,ll3,arcl = lowZ.section_lengths(wlow,glow)
# lengths_low=[ll1,ll2,ll3,arcl]

# lh1,lh2,lh3,arch = highZ.section_lengths(whigh,ghigh)
# lengths_high=[lh1,lh2,lh3,arch]

# xrm1,yrm1 = [coords(xb_strt,-rmw/2+wc/2),coords(yb_strt)]
# rm = [rmlZ.mirror_removes(xrm1,yrm1,lengths_low)]

# xrm2,yrm2 = [coords(xrm1,-wlow+lowZ.mirror_width()),coords(yb_strt)]
# rm += [rmhZ.mirror_removes(xrm2,yrm2,lengths_high)]

# xrm3,yrm3 = [coords(xrm2,-whigh+highZ.mirror_width()),coords(yb_strt)]
# rm += [rmlZ.mirror_removes(xrm3,yrm3,lengths_low)]

# xrm4,yrm4 = [coords(xrm3,-wlow+lowZ.mirror_width()),coords(yb_strt)]
# rm += [rmhZ.mirror_removes(xrm4,yrm4,lengths_high)]

# xrm5,yrm5 = [coords(xrm4,-whigh+highZ.mirror_width()),coords(yb_strt)]
# rm += [rmlZ.mirror_removes(xrm5,yrm5,lengths_low)]

# xrm6,yrm6 = [coords(xrm5,-wlow+lowZ.mirror_width()),coords(yb_strt)]
# rm += [rmhZ.mirror_removes(xrm6,yrm6,lengths_high)]

# xrm7,yrm7 = [coords(xrm6,-whigh+highZ.mirror_width()),coords(yb_strt)]
# rm += [rmlZ.mirror_removes(xrm7,yrm7,lengths_low)]

# xrm8,yrm8 = [coords(xrm7,-wlow+lowZ.mirror_width()),coords(yb_strt)]
# rm += [rmhZ.mirror_removes(xrm8,yrm8,lengths_high)]

# for i in range(0, np.shape(lz)[0]):
# 	for j in range(0, np.shape(lz)[1]):
# 		mirror_lz = gdspy.Polygon(lz[i][j],1)
# 		mirror_hz = gdspy.Polygon(hz[i][j],1)
# 		poly_cell.add(mirror_lz)
# 		poly_cell.add(mirror_hz)

# for i in range(0, np.shape(rm)[0]):
# 	for j in range(0, np.shape(rm)[1]):
# 		mirror_rm = gdspy.Polygon(rm[i][j],2)
# 		substrate = gdspy.fast_boolean(substrate,mirror_rm, 'not', 
# 		precision=1e-9, max_points=1000, layer=0)

# # UPPER BRAGG SECTIONS
# ######################

# xlz1,ylz1 = [coords(xb_strt+wc/2-wlow/2),coords(cav_y4,-lcav1)]
# lz = [lowZ.rotate_mirror(xlz1,ylz1, w_remove=wc, g_remove=gc)]

# xhz1,yhz1 = [coords(xlz1-wlow/2-whigh/2+lowZ.mirror_width()),coords(ylz1)]
# hz = [highZ.rotate_mirror(xhz1,yhz1, w_remove=wc, g_remove=gc)]

# xlz2,ylz2 = [coords(xhz1-whigh/2-wlow/2+highZ.mirror_width()),coords(yhz1)]
# lz += [lowZ.rotate_mirror(xlz2,ylz2, w_remove=wc, g_remove=gc)]

# xhz2,yhz2 = [coords(xlz2-wlow/2-whigh/2+lowZ.mirror_width()),coords(ylz1)]
# hz += [highZ.rotate_mirror(xhz2,yhz2, w_remove=wc, g_remove=gc)]

# xlz3,ylz3 = [coords(xhz2-whigh/2-wlow/2+highZ.mirror_width()),coords(yhz1)]
# lz += [lowZ.rotate_mirror(xlz3,ylz3, w_remove=wc, g_remove=gc)]

# xhz3,yhz3 = [coords(xlz3-wlow/2-whigh/2+lowZ.mirror_width()),coords(ylz1)]
# hz += [highZ.rotate_mirror(xhz3,yhz3, w_remove=wc, g_remove=gc)]

# xlz4,ylz4 = [coords(xhz3-whigh/2-wlow/2+highZ.mirror_width()),coords(yhz1)]
# lz += [lowZ.rotate_mirror(xlz4,ylz4, w_remove=wc, g_remove=gc)]

# xhz4,yhz4 = [coords(xlz4-wlow/2-whigh/2+lowZ.mirror_width()),coords(ylz1)]
# hz += [highZ.rotate_mirror(xhz4,yhz4, w_remove=wc, g_remove=gc)]

# for i in range(0, np.shape(lz)[0]):
# 	for j in range(0, np.shape(lz)[1]):
# 		mirror_lz = gdspy.Polygon(lz[i][j],1)
# 		mirror_hz = gdspy.Polygon(hz[i][j],1)
# 		poly_cell.add(mirror_lz)
# 		poly_cell.add(mirror_hz)

# # UPPER BRAGG SECTION REMOVES
# #############################

# xrm1,yrm1 = [coords(xb_strt,-rmw/2+wc/2),coords(ylz1)]
# rm = [rmlZ.rotate_mirror_removes(xrm1,yrm1,lengths_low)]

# xrm2,yrm2 = [coords(xrm1,-wlow+lowZ.mirror_width()),coords(ylz1)]
# rm += [rmhZ.rotate_mirror_removes(xrm2,yrm2,lengths_high)]

# xrm3,yrm3 = [coords(xrm2,-whigh+highZ.mirror_width()),coords(ylz1)]
# rm += [rmlZ.rotate_mirror_removes(xrm3,yrm3,lengths_low)]

# xrm4,yrm4 = [coords(xrm3,-wlow+lowZ.mirror_width()),coords(ylz1)]
# rm += [rmhZ.rotate_mirror_removes(xrm4,yrm4,lengths_high)]

# xrm5,yrm5 = [coords(xrm4,-whigh+highZ.mirror_width()),coords(ylz1)]
# rm += [rmlZ.rotate_mirror_removes(xrm5,yrm5,lengths_low)]

# xrm6,yrm6 = [coords(xrm5,-wlow+lowZ.mirror_width()),coords(ylz1)]
# rm += [rmhZ.rotate_mirror_removes(xrm6,yrm6,lengths_high)]

# xrm7,yrm7 = [coords(xrm6,-whigh+highZ.mirror_width()),coords(ylz1)]
# rm += [rmlZ.rotate_mirror_removes(xrm7,yrm7,lengths_low)]

# xrm8,yrm8 = [coords(xrm7,-wlow+lowZ.mirror_width()),coords(ylz1)]
# rm += [rmhZ.rotate_mirror_removes(xrm8,yrm8,lengths_high)]

# for i in range(0, np.shape(rm)[0]):
# 	for j in range(0, np.shape(rm)[1]):
# 		mirror_rm = gdspy.Polygon(rm[i][j],2)
# 		substrate = gdspy.fast_boolean(substrate,mirror_rm, 'not', 
# 		precision=1e-9, max_points=1000, layer=0)


# # FEEDLINE SECTIONS
# ####################################################################

# # LOWER FEED 
# #
# l1, l2, l3, arc = highZ.section_lengths(wc,gc)
# cc, ratio, bond_pad, rfeed = [2*ghigh, .5, 400, 100]
# feedin_length, feedlink_length, feed_st_length = [100,685,1600]
# rstrt = rlow + 100
# rlow = 100

# # Low Z feedline sections
# #
# xf0Low = xhz4 + highZ.mirror_width() - wlow/2 - whigh/2#xb_strt + no_periods*(lowZ.mirror_width() + highZ.mirror_width())
# yf0Low = yb_strt
# feedline = [rs.rect(wlow,l1,xf0Low,yf0Low)]

# xf1Low,yf1Low = [coords(xf0Low,rstrt+wlow),coords(yf0Low,l1)]
# feedline += [rs.halfarc(rstrt,wlow,xf1Low, yf1Low,orientation='N',npoints=40)]

# xf2Low,yf2Low = [coords(xf1Low,rstrt),coords(yf1Low)]
# feedline += [rs.rect(wlow,-l2,xf2Low,yf2Low)]

# xf3Low,yf3Low = [coords(xf2Low),coords(yf2Low,-l2)]
# feedline += [rs.rect(wlow,-l3/4,xf3Low,yf3Low)]

# xf4Low,yf4Low = [coords(xf3Low,-rlow),coords(yf3Low,-l3/4)]
# feedline += [rs.quarterarc(rlow,wlow,xf4Low,yf4Low,orientation='SE',npoints=20)]

# xf5Low,yf5Low = [coords(xf4Low,-3*l3/4-arc/2+230),coords(yf4Low, - rlow - wlow)]
# feedline += [rs.rect(3*l3/4+arc/2-230,wlow,xf5Low,yf5Low)]

# # High Z feedline sections
# #
# xf0High,yf0High = [coords(xf5Low,-l2-733/2),coords(yf5Low,+wlow/2-whigh/2)]
# feedline += [rs.rect(l2+733/2,whigh,xf0High,yf0High)]

# xf1High,yf1High = [coords(xf0High),coords(yf0High,-rhigh)]
# feedline += [rs.halfarc(rhigh,whigh,xf1High, yf1High,orientation='W',npoints=40)]

# xf2High,yf2High = [coords(xf1High),coords(yf1High,-rhigh - whigh)]
# feedline += [rs.rect(l3+l1-733/2,whigh,xf2High,yf2High)]

# xf3High,yf3High = [coords(xf2High,l3+l1-733/2),coords(yf2High,-rhigh)]
# feedline += [rs.quarterarc(rhigh,whigh,xf3High,yf3High,orientation='NE',npoints=20)]

# xf4High,yf4High = [coords(xf3High,rhigh),coords(yf3High,-arc/2)]
# feedline += [rs.rect(whigh,arc/2,xf4High,yf4High)]

# for i in range(0,np.shape(feedline)[0]):
# 	feed = gdspy.Polygon(feedline[i],1)
# 	poly_cell.add(feed)

# # Lower Feedbond
# #
# xf5High,yf5High = [coords(xf4High,-2*whigh-4*ghigh),coords(yf4High-arc/2)]

# H=400
# w = H*(1 + 2*.5)
# l = H*.5

# xbond, ybond = [coords(xf4High),coords(yf4High)]
# feedbond = [rs.triangle(xbond+whigh,ybond,xbond,ybond,
# 	xbond-400,ybond-300,xbond+400,ybond-300)]


# # LOWER FEEDLINE REMOVES
# ########################
# # Low Z feedline removes
# #

# rstrt = rstrt - 7.185
# xf0Low = xhz4 + highZ.mirror_width() - rmw/2 - 1
# yf0Lowr = yf0Low
# feedline_remove = [rs.rect(rmw,l1,xf0Low,yf0Low)]

# xf1Low,yf1Low = [coords(xf0Low,rstrt+rmw),coords(yf0Low,l1)]
# feedline_remove += [rs.halfarc(rstrt,rmw,xf1Low, yf1Low,orientation='N',npoints=40)]

# xf2Low,yf2Low = [coords(xf1Low,rstrt),coords(yf1Low)]
# feedline_remove += [rs.rect(rmw,-l2,xf2Low,yf2Low)]

# xf3Low,yf3Low = [coords(xf2Low),coords(yf2Low,-l2)]
# feedline_remove += [rs.rect(rmw,-l3/4,xf3Low,yf3Low)]

# rstrt = rstrt + 39
# xf4Low,yf4Low = [coords(xf3Low,-rstrt/2),coords(yf3Low,-l3/4)]
# feedline_remove += [rs.quarterarc(rstrt/2,rmw,xf4Low,yf4Low,orientation='SE',npoints=20)]

# xf5Low,yf5Low = [coords(xf4Low,-3*l3/4-arc/2+230),coords(yf4Low, - rstrt/2 - rmw)]
# feedline_remove += [rs.rect(3*l3/4+arc/2-230,rmw,xf5Low,yf5Low)]

# # High Z feedline removes
# #
# xf0High,yf0High = [coords(xf5Low,-l2-733/2),coords(yf5Low)]
# feedline_remove += [rs.rect(l2+733/2,rmw,xf0High,yf0High)]

# rharc = 34.05
# xf1High,yf1High = [coords(xf0High),coords(yf0High,-rharc)]
# feedline_remove += [rs.halfarc(rharc,rmw,xf1High, yf1High,orientation='W',npoints=40)]

# xf2High,yf2High = [coords(xf1High),coords(yf1High,-rharc - rmw)]
# feedline_remove += [rs.rect(l3+l1-733/2,rmw,xf2High,yf2High)]

# xf3High,yf3High = [coords(xf2High,l3+l1-733/2),coords(yf2High,-rharc)]
# feedline_remove += [rs.quarterarc(rharc,rmw,xf3High,yf3High,orientation='NE',npoints=20)]

# xf4High,yf4High = [coords(xf3High,rharc),coords(yf3High,-arc/2)]
# feedline_remove += [rs.rect(rmw,arc/2,xf4High,yf4High)]

# xbond, ybond = [coords(xf4High),coords(yf4High)]
# feedline_remove += [rs.triangle(xbond+rmw,ybond,xbond,ybond,
# 	xbond-440,ybond-320,xbond+480,ybond-320)]

# # UPPER FEED 
# #
# # Low Z feedline sections
# #
# xf0Low = xhz4 + highZ.mirror_width() - wlow/2 - whigh/2#xb_strt + no_periods*(lowZ.mirror_width() + highZ.mirror_width())
# yf0Low = yhz4
# feedline = [rs.rect(wlow,-l1,xf0Low,yf0Low)]

# xf1Low,yf1Low = [coords(xf0Low,rstrt+wlow),coords(yf0Low,-l1)]
# feedline += [rs.halfarc(rstrt,wlow,xf1Low, yf1Low,orientation='S',npoints=40)]

# xf2Low,yf2Low = [coords(xf1Low,rstrt),coords(yf1Low)]
# feedline += [rs.rect(wlow,l2,xf2Low,yf2Low)]

# xf3Low,yf3Low = [coords(xf2Low),coords(yf2Low,l2)]
# feedline += [rs.rect(wlow,l3/4,xf3Low,yf3Low)]

# xf4Low,yf4Low = [coords(xf3Low,-rlow),coords(yf3Low,l3/4)]
# feedline += [rs.quarterarc(rlow,wlow,xf4Low,yf4Low,orientation='NE',npoints=20)]

# xf5Low,yf5Low = [coords(xf4Low,-3*l3/4-arc/2+230),coords(yf4Low, + rlow)]
# feedline += [rs.rect(3*l3/4+arc/2-230,wlow,xf5Low,yf5Low)]

# # High Z feedline sections
# #
# xf0High,yf0High = [coords(xf5Low,-l2-733/2),coords(yf5Low,+wlow/2-whigh/2)]
# feedline += [rs.rect(l2+733/2,whigh,xf0High,yf0High)]

# xf1High,yf1High = [coords(xf0High),coords(yf0High,rhigh+whigh)]
# feedline += [rs.halfarc(rhigh,whigh,xf1High, yf1High,orientation='W',npoints=40)]

# xf2High,yf2High = [coords(xf1High),coords(yf1High,+rhigh)]
# feedline += [rs.rect(l3+l1-733/2,whigh,xf2High,yf2High)]

# xf3High,yf3High = [coords(xf2High,l3+l1-733/2),coords(yf2High,rhigh+whigh)]
# feedline += [rs.quarterarc(rhigh,whigh,xf3High,yf3High,orientation='SE',npoints=20)]

# xf4High,yf4High = [coords(xf3High,rhigh),coords(yf3High,arc/2)]
# feedline += [rs.rect(whigh,-arc/2,xf4High,yf4High)]

# xbond, ybond = [coords(xf4High),coords(yf4High)]
# feedline += [rs.triangle(xbond,ybond,xbond+whigh,ybond,
# 	xbond+400,ybond+300,xbond-400,ybond+300)]

# for i in range(np.shape(feedline)[0]):
# 	feed = gdspy.Polygon(feedline[i],1)
# 	poly_cell.add(feed)

# # UPPER FEEDLINE REMOVES
# ########################
# # Low Z feedline removes
# #

# rstrt = rstrt - 7.185
# xf0Low = xhz4 + highZ.mirror_width() - rmw/2-1
# yf0Lowr = yf0Low
# feedline_remove += [rs.rect(rmw,-l1,xf0Low,yf0Low)]

# xf1Low,yf1Low = [coords(xf0Low,rstrt+rmw),coords(yf0Low,-l1)]
# feedline_remove += [rs.halfarc(rstrt,rmw,xf1Low, yf1Low,orientation='S',npoints=40)]

# xf2Low,yf2Low = [coords(xf1Low,rstrt),coords(yf1Low)]
# feedline_remove += [rs.rect(rmw,l2,xf2Low,yf2Low)]

# xf3Low,yf3Low = [coords(xf2Low),coords(yf2Low,l2)]
# feedline_remove += [rs.rect(rmw,l3/4,xf3Low,yf3Low)]

# rstrt = rstrt+7.185
# xf4Low,yf4Low = [coords(xf3Low,-rstrt/2),coords(yf3Low,l3/4)]
# feedline_remove += [rs.quarterarc(rstrt/2,rmw,xf4Low,yf4Low,orientation='NE',npoints=20)]

# xf5Low,yf5Low = [coords(xf4Low,-3*l3/4-arc/2+230),coords(yf4Low, + rstrt/2)]
# feedline_remove += [rs.rect(3*l3/4+arc/2-230,rmw,xf5Low,yf5Low)]

# # High Z feedline removes
# #
# xf0High,yf0High = [coords(xf5Low,-l2-733/2),coords(yf5Low)]
# feedline_remove += [rs.rect(l2+733/2,rmw,xf0High,yf0High)]

# rharc = 34.05
# xf1High,yf1High = [coords(xf0High),coords(yf0High,rharc+rmw)]
# feedline_remove += [rs.halfarc(rharc,rmw,xf1High, yf1High,orientation='W',npoints=40)]

# xf2High,yf2High = [coords(xf1High),coords(yf1High,rharc)]
# feedline_remove += [rs.rect(l3+l1-733/2,rmw,xf2High,yf2High)]

# xf3High,yf3High = [coords(xf2High,l3+l1-733/2),coords(yf2High,rharc+rmw)]
# feedline_remove += [rs.quarterarc(rharc,rmw,xf3High,yf3High,orientation='SE',npoints=20)]

# xf4High,yf4High = [coords(xf3High,rharc),coords(yf3High,arc/2)]
# feedline_remove += [rs.rect(rmw,-arc/2,xf4High,yf4High)]

# xbond, ybond = [coords(xf4High),coords(yf4High)]
# feedline_remove += [rs.triangle(xbond,ybond,xbond+rmw,ybond,
# 	xbond+480,ybond+320,xbond-440,ybond+320)]

# # for i in range(np.shape(feedline_remove)[0]):
# # 	feed = gdspy.Polygon(feedline_remove[i],2)
# # 	poly_cell.add(feed)

# ###########

# ################
# for i in range(0, np.shape(feedline_remove)[0]):
# 	feed_rm = gdspy.Polygon(feedline_remove[i],2)
# 	substrate = gdspy.fast_boolean(substrate,feed_rm, 'not', 
# 		precision=1e-9, max_points=1000, layer=0)

# for i in range(0,np.shape(feedbond)[0]):
# 	bond = gdspy.Polygon(feedbond[i],1)
# 	poly_cell.add(bond)

poly_cell.add(substrate)


###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
