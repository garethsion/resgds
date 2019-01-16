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
layout_file ='design.gds'

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
xb_strt,yb_strt = [coords(400),coords(sub_y/2)- lext2 - lext3 - 100]
lcav1, lcav2, lcav3 = [1000, 5500, 1000]
taper_length = 100

cavity = Trench(wc, gc, poly_cell, layer = 2)

cav_x0,cav_y0 = [coords(xb_strt),coords(yb_strt,-lcav1)]
strait = cavity.straight_trench(lcav1-taper_length, cav_x0, cav_y0, orient='V')

cav_xtaper, cav_ytaper = [coords(xb_strt),coords(yb_strt,-taper_length)]

# cavity.thinning_trench(w1, w2, rat, cav_xtaper, cav_ytaper, 
#         taper_length, orientation='N',strait=strait)

cavity.taper(wc, gc, wlow, glow, cav_x0, 
        cav_y0+lcav1-taper_length, cav_x0, cav_y0+lcav1)

cav_x1,cav_y1 = [coords(xb_strt,-rlow),coords(yb_strt,-lcav1)]
cavity.halfarc_trench(rlow,cav_x1,cav_y1,orient='S',npoints=40)

cav_x2,cav_y2 = [coords(xb_strt,-2*rlow-wlow-2*glow),coords(yb_strt,-lcav1)]
cavity.straight_trench(lcav2,cav_x2,cav_y2,orient='V')

cav_x3,cav_y3 = [coords(xb_strt,-rlow),coords(yb_strt,lcav2-lcav1)]
cavity.halfarc_trench(rlow,cav_x3,cav_y3,orient='N',npoints=40)

cav_x4,cav_y4 = [coords(xb_strt),coords(yb_strt,lcav2-lcav1-lcav3+taper_length)]
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
yb_strtr = cavend[1][0][1] - taper_length

make_lowZ = lambda i: lowZ.rotate_mirror2(xb_strtr + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strtr,w_remove=wc, g_remove=gc)

make_highZ = lambda i: highZ.rotate_mirror2(xb_strtr + arr_h[i]*highZ.mirror_width()
        + arr_l[i]*lowZ.mirror_width(), yb_strtr,w_remove=wc, g_remove = gc)

[make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 0]
[make_highZ(x) for x in range(len(arr_l)) if x % 2 == 1]

# Feedline sections [layer 2]

l1, l2, l3, arc = highZ.section_lengths(wc,gc)
cc, ratio, bond_pad, rfeed = [2*gc, .5, 400, 100]

feedline = Trench(wlow,glow,poly_cell, layer=2)
feedin_length, feedlink_length, feed_st_length = [100,685,1600]

xf0 = highZ.get_mirror_coordinates()[1][0]
yf0 = highZ.get_mirror_coordinates()[1][1]
fht_strait = feedline.straight_trench(l1,xf0,yf0,orient='V')

xf1,yf1 = [coords(xf0,rlow+2*gc+wc),coords(yf0,l1)]
feed_harctrL = feedline.halfarc_trench(rlow,xf1, yf1,orient='N',npoints=40)

xf2,yf2 = [coords(xf1,rlow),coords(yf1)]
fht_strait = feedline.straight_trench(-l2,xf2,yf2,orient='V')

xf3,yf3 = [coords(xf2),coords(yf2,-l2)]
fht_strait = feedline.straight_trench(-l3/2,xf3,yf3,orient='V')

xf4,yf4 = [coords(xf3,-rlow),coords(yf3,-l3/2)]
feed_qarctrL = feedline.quarterarc_trench(rlow,xf4,yf4,orient='SE',npoints=20)

xf5,yf5 = [coords(xf4,-l3/2-arc/2),coords(yf4,-2*glow - wlow - rlow)]
fht_strait = feedline.straight_trench(l3/2+arc/2,xf5,yf5,orient='H')

print(2*glow + wlow +rlow)
#feed_harctrL = feedline.halfarc_trench(rfeed,xf1, yf1,orient='N',npoints=40)


#####

# # Feedline sections [layer 2]
# ############################################################################

# #Lower feedline
# feedline = Trench(wc,gc,poly_cell, layer=2)

# cc, ratio, bond_pad, rfeed = [2*gc, .5, 400, 100]
# feedin_length, feedlink_length, feed_st_length = [100,685,1600]

# xf0 = highZ.get_mirror_coordinates()[1][0]
# yf0 = highZ.get_mirror_coordinates()[1][1]

# xf1,yf1 = [coords(xf0,rfeed+2*gc+wc),coords(yf0)]
# feed_harctrL = feedline.halfarc_trench(rfeed,xf1, yf1,orient='N',npoints=40)


# xf2,yf2 = [coords(xf1,rfeed),coords(yf1)]
# fht_strait = feedline.straight_trench(-feed_st_length,xf2,yf2,orient='V')

# # Lower feedbond
# xf3,yf3 = [coords(xf2,-2*wc-4*gc),coords(yf2 - feed_st_length)]
# feed_rhs = LayoutComponents(poly_cell, xf3, yf3, width=wc, gap = gc, layer=2)
# feedbond = feed_rhs.make_feedbond(feedin_length,cc, ratio, 
#         bond_pad, fht_strait[0][3][0], fht_strait[0][3][1], orientation='N')

# # Upper feedline
# xf0U = highZ.get_rotated_mirror_coordinates()[1][0]
# yf0U = highZ.get_rotated_mirror_coordinates()[1][1]

# xf1U,yf1U = [coords(xf0U,rfeed+2*gc+wc),coords(yf0U)]
# feed_harctrU = feedline.halfarc_trench(rfeed,xf1U, yf1U,orient='S',npoints=40)

# npts = int(np.shape(feed_harctrU)[1]/2)
# xf2U,yf2U = [coords(feed_harctrU[0][npts-1][0]),coords(yf0U)]
# fhtU_strait = feedline.straight_trench(feed_st_length,xf2U,yf2U,orient='V')

# # Upper feedbond
# xf3U,yf3U = [coords(xf2U,-2*wc-4*gc),coords(yf2U+feed_st_length)]
# feed_lhs = LayoutComponents(poly_cell, xf3U,yf3U, width=wc, gap = gc, layer=2)
# feedbond = feed_lhs.make_feedbond(feedin_length,cc, ratio, bond_pad, 
# 	xf2U, yf3U, orientation='S')

# # Feedline removes [layer 3]
# ############################################################################

# # Lower feed removes
# x1_fdRem_L, y1_fdRem_L = [coords(xf2,-rm_width/2 + wc/2 + gc),coords(yf0)]
# feed_remove_L = BuildRect(poly_cell,rm_width, -feed_st_length - feedin_length, layer = 3)
# fs_remove_L = feed_remove_L.make(x1_fdRem_L,y1_fdRem_L,layer=3)

# rad_feed = .5*(x1_fdRem_L - (xf0 + .5*(whigh + 2*ghigh) + rm_width/2))

# feed_xhfrL, feed_yhfrL = [coords(x1_fdRem_L - rad_feed),coords(yf1)]
# feed_harc_remove = rs.make_halfarc(rad_feed, rm_width,
# 	feed_xhfrL, feed_yhfrL, orientation='N', npoints=40, layer=3) 

# feed_remove = feed_rhs.make_feedbond_remove(feedin_length,cc, ratio, 
#         bond_pad, x1_fdRem_L,feed_yhfrL-feed_st_length,x1_fdRem_L,
#         feed_yhfrL-feed_st_length,x1_fdRem_L+rm_width, orientation='N')

# # Upper feed removes
# x1_fdRem_U, y1_fdRem_U = [coords(xf2U,-rm_width/2 + wc/2 + gc),coords(yf0U)]
# feed_remove_U = BuildRect(poly_cell,rm_width, feed_st_length + feedin_length, layer = 3)
# fs_remove_U = feed_remove_U.make(x1_fdRem_U,y1_fdRem_U,layer=3)

# feed_xhfrU, feed_yhfrU = [coords(x1_fdRem_L - rad_feed),coords(yf1U)]
# feed_harc_remove = rs.make_halfarc(rad_feed, rm_width,
# 	feed_xhfrU, feed_yhfrU, orientation='S', npoints=40, layer=3) 

# feed_remove = feed_rhs.make_feedbond_remove(feedin_length,cc, ratio, 
#         bond_pad, x1_fdRem_U,feed_yhfrU+feed_st_length,x1_fdRem_L,
#         feed_yhfrU+feed_st_length,x1_fdRem_U+rm_width, orientation='S')

###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
