#!/usr/bin/env python

""" 
This modification of the Bragg resonator generator has a smaller footprint. 
This is to make the fabrication process easier, since I have had problems with
fitting the device onto the 10x5 chips.

I have also endeavoured to clean up the fabrication file, because I became unhappy 
with how untidy the code was. this is the start of the refactoring process.
"""

import os
from resgds import *
# import braggresonator
from interface import Interface
import gdspy # gds library
import numpy as np


def bragg_mirror(w,g,r,l,x0,y0,cell):
        """
            Defines a quarterwave Bragg mirror section.
        """
        coords = lambda x,dx=0: x+dx
        
        l1, l2, l3, arc = lengths(w,g,r,l)
        rs = Shapes(cell)

        # Make Bragg mirror sections
        #
        bragg = rs.straight_trench(l1, w, g,x0, y0, orientation='V')

        x1,y1 = [coords(x0,w+2*g+r), coords(y0,l1)]
        bragg += rs.halfarc_trench(r, w, g, x1, y1, orient='N', npoints=40)

        x2,y2 = [coords(x1,r), coords(y1,-l2)]
        bragg += rs.straight_trench(l2,w,g,x2,y2,orientation='V')

        x3,y3 = [coords(x2,w+2*g+r), coords(y2)]
        bragg += rs.halfarc_trench(r, w,g,x3, y3, orient='S', npoints=40)

        x4,y4 = [coords(x3,r), coords(y3)] 
        bragg += rs.straight_trench(l3,w,g,x4,y4,orientation='V')

        return bragg

def rotate_mirror(w,g,r,l,x0,y0,cell):
    """
        Defines a quarterwave Bragg mirror section.
    """
    coords = lambda x,dx=0: x+dx
    
    l1, l2, l3, arc = lengths(w,g,r,l)
    rs = Shapes(cell)

    # Make Bragg mirror sections
    #   
    # bragg = self.__mirror.straight_trench(l1, x0, y0-l1, orient='V')
    bragg = rs.straight_trench(-l1,w,g,x0,y0, orientation='V')
    
    x1,y1 = [coords(x0,w+2*g+r), coords(y0,-l1)]
    bragg += rs.halfarc_trench(r,w,g,x1,y1, orient='S', npoints=40)

    x2,y2 = [coords(x1,r), coords(y1)]
    bragg += rs.straight_trench(l2,w,g,x2,y2,orientation='V')

    x3,y3 = [coords(x2,w+2*g+r), coords(y2,l2)]
    bragg += rs.halfarc_trench(r,w,g,x3,y3, orient='N', npoints=40)

    x4,y4 = [coords(x3,r), coords(y3,-l3)]
    bragg += rs.straight_trench(l3,w,g,x4,y4,orientation='V')

    return bragg


def bragg_mirror_remove(w,g,r,l,x0,y0,cell):
    # Make remove sections
    #
    rm_width = 4*w + 2*g
    l1, l2, l3, arc = lengths(w,g,r,l)
    arcrad = .5*(2*r - g - w)
    rs = Shapes(cell)

    xrm0, yrm0 = [coords(x0-rm_width/2 + w/2+g),coords(y0)]
    remove = [rs.rect(rm_width,l1, xrm0, yrm0)]

    xrm1, yrm1 = [coords(xrm0,arcrad+rm_width),coords(yrm0,l1)]
    remove += [rs.halfarc(arcrad, rm_width, xrm1, yrm1, 
    orientation='N', npoints=40)] 

    xrm2, yrm2 = [coords(xrm1,arcrad),coords(yrm1)]
    remove += [rs.rect(rm_width,-l2, xrm2,yrm2)]

    xrm3, yrm3 = [coords(xrm2,arcrad+rm_width),coords(yrm2,-l2)]
    remove += [rs.halfarc(arcrad, rm_width, xrm3, yrm3, 
    orientation='S', npoints=40)] 

    xrm4, yrm4 = [coords(xrm3,arcrad),coords(yrm3)]
    remove += [rs.rect(rm_width,l3, xrm4,yrm4)]

    return remove


def lengths(w,g,r,l):
    out_LHS = g
    out_RHS = 2*w + 3*g + 2*r 
        
    diameter = out_RHS - out_LHS - (w/2)
    
    arclength = .5 * diameter * np.pi
    arctot = 2*arclength
    len_remain = l - arctot

    l1 = len_remain/6
    l2 = 3*l1
    l3 = 2*l1
    return l1, l2, l3, arclength

def mirror_width(w,g,r):
    """
        Method which calculates the total width of the Bragg mirror half period 
    """
    width = 2*(w + 2*g + 2*r)
    return width

def remove_width(w,g,r):
    """
        Method which calculates the total width of the Bragg mirror half period 
    """
    rm_width = 4*w + 2*g
    arcrad = .5*(2*r - g - w)
    width = 3*rm_width + 4*arcrad
    return width

# Layout filename
layout_file ='Bragg_test.gds'

# Parameters
###################################################################
sub_x, sub_y = [4000, 9000] # substrate dimensions
wc, gc, lc = [8.11, 17.85, 8108.45] # Cavity width, gap, length
wlow, llow = [30.44, 4051.32]  # Low Z section
whigh, lhigh = [2, 4051.32] # High Z section
glow, ghigh = [.5*(wc + 2*gc - wlow),.5*(wc + 2*gc - whigh)]
wtot = 2*gc+wc

sub_layer = 0
dot_layer = 1
cond_layer = 2
remove_layer = 3

rharc = 55 # halfarc radius
rqarc = 100 # quarterarc radius

conductor = []

# Select polarity of the mirrors
###################################################################
w1,g1 = [wlow,glow]
w2,g2 = [whigh,ghigh]
l1,l2 = [llow,lhigh]

lbragg1, lbragg2, lbragg3, arcbragg = lengths(w1,g1,rharc,l1)
lci, lcii, lciii, arcc = lengths(wc,gc,rharc,lc)

# Start making resonator geometry
############################################################################

# Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# Substrate [layer 0]
sub = [rs.rect(sub_x,sub_y,0,0)]

for i in range(0,len(sub)):
	sub = gdspy.Polygon(sub[i],sub_layer)
	# conductor = gdspy.fast_boolean(conductor,cavity, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(sub)

# Antidot array [layer 1]
layout = LayoutComponents(poly_cell, sub_x, sub_y,layer=dot_layer)
dots = layout.antidot_array(0,0,10,30,0)

for i in range(0,len(dots)):
	antidots = gdspy.Polygon(dots[i],dot_layer)
	# conductor = gdspy.fast_boolean(conductor,cavity, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(antidots)

# CAVITY
############################################################################
coords = lambda x,dx=0: x+dx
x0,y0 = [coords(725),coords(sub_y/2-997)]

taper_length = 80
lbragg3 = lbragg3 - taper_length

cav_xtaper, cav_ytaper = [coords(x0),coords(y0)]
xr = x0 + 2*g1 + w1
taperL = [ (x0,y0), (x0+g1, y0), (x0+gc,y0-taper_length),(x0,y0-taper_length)]
taperR = [ (xr,y0), (xr-g1, y0), (xr-gc,y0-taper_length),(xr,y0-taper_length)]
cav = [taperL,taperR]

cav_x0,cav_y0 = [coords(x0),coords(y0,-lbragg3-taper_length)]
cav += rs.straight_trench(lbragg3,wc,gc, cav_x0, cav_y0, orientation='V')

cav_x1,cav_y1 = [coords(cav_x0,-rharc),coords(cav_y0,)]
cav += rs.halfarc_trench(rharc,wc,gc,cav_x1,cav_y1,orient='S',npoints=40)

cav_x2,cav_y2 = [coords(cav_x1,-rharc-wtot),coords(cav_y1)]
cav += rs.straight_trench(2*lbragg2 + 2*lbragg1 + 2*arcbragg - 2*taper_length,wc,gc,cav_x2,cav_y2,orientation='V')

cav_x3,cav_y3 = [coords(cav_x2,rharc+wtot),coords(cav_y2,2*lbragg2 + 2*lbragg1+2*arcbragg - 2*taper_length)]
cav += rs.halfarc_trench(rharc,wc,gc,cav_x3,cav_y3,orient='N',npoints=40)

cav_x4,cav_y4 = [coords(cav_x3,rharc),coords(cav_y3)]
cav += rs.straight_trench(-lbragg3,wc,gc,cav_x4,cav_y4,orientation='V')

cav_x5,cav_y5 = [coords(cav_x4),coords(cav_y4,-lbragg3)]
taperL = [ (cav_x5,cav_y5-taper_length), (cav_x5+g1, cav_y5-taper_length), (cav_x5+gc,cav_y5),(cav_x5,cav_y5)]
taperR = [ (xr,cav_y5-taper_length), (xr-g1, cav_y5-taper_length), (xr-gc,cav_y5),(xr,cav_y5)]
cav += [taperL,taperR]

for i in range(0,len(cav)):
	cavity = gdspy.Polygon(cav[i],cond_layer)
	# conductor = gdspy.fast_boolean(conductor,cavity, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(cavity)

# BRAGG MIRRORS
##########################################################################
no_periods = 4
# bragg = bragg_mirror(w1,g1,rharc,l1,x0,y0,poly_cell)

# Vectors to store shifting numbers for making mirrors
arr_l = np.repeat(np.arange(0,no_periods),2*np.ones(no_periods,dtype=int))
arr_h = np.append(arr_l[1:],[no_periods], axis=0)

# MAKE LOWER BRAGG MIRRORS
#-------------------------
make_lowZ = lambda i: bragg_mirror(w1,g1,rharc,l1,x0 + arr_h[i]*mirror_width(w1,g1,rharc)
        + arr_l[i]*mirror_width(w2,g2,rharc), y0, poly_cell)

make_highZ = lambda i: bragg_mirror(w2,g2,rharc,l2,x0 + arr_h[i]*mirror_width(w1,g1,rharc)
        + arr_l[i]*mirror_width(w2,g2,rharc), y0, poly_cell)

bragg = [make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 0]
bragg += [make_highZ(x) for x in range(len(arr_l)) if x % 2 == 1]

for i in range(np.shape(bragg)[0]):
	for j in range(np.shape(bragg)[1]):
		braggs = gdspy.Polygon(bragg[i][j],cond_layer)
		conductor = gdspy.fast_boolean(conductor,braggs, 'or', 
			precision=1e-9, max_points=1000, layer=cond_layer)
		poly_cell.add(braggs)

# # MAKE LOWER BRAGG REMOVES
# #-------------------------
# make_lowZr = lambda i: bragg_mirror_remove(wc,gc,rharc,l1,x0 
# 	+ arr_h[i]*remove_width(w1,g1,rharc)
#     + arr_l[i]*remove_width(w2,g2,rharc), y0, poly_cell)

# make_highZr = lambda i: bragg_mirror_remove(wc,gc,rharc,l2,x0 
# 	+ arr_h[i]*remove_width(w1,g1,rharc)
#     + arr_l[i]*remove_width(w2,g2,rharc), y0, poly_cell)

# bragg_rem = [make_lowZr(x) for x in range(len(arr_l)) if x % 2 == 0]
# bragg_rem += [make_highZr(x) for x in range(len(arr_l)) if x % 2 == 1]

# for i in range(np.shape(bragg_rem)[0]):
# 	for j in range(np.shape(bragg_rem)[1]):
# 		braggr = gdspy.Polygon(bragg_rem[i][j],remove_layer)
# 		poly_cell.add(braggr)


# MAKE LOWER BRAGG MIRRORS
#-------------------------
x0u = x0
y0u = cav_y5 - taper_length

make_lowZ = lambda i: rotate_mirror(w1,g1,rharc,l1,x0u + arr_h[i]*mirror_width(w1,g1,rharc)
        + arr_l[i]*mirror_width(w2,g2,rharc), y0u, poly_cell)

make_highZ = lambda i: rotate_mirror(w2,g2,rharc,l2,x0u + arr_h[i]*mirror_width(w1,g1,rharc)
        + arr_l[i]*mirror_width(w2,g2,rharc), y0u, poly_cell)

bragg = [make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 0]
bragg += [make_highZ(x) for x in range(len(arr_l)) if x % 2 == 1]

for i in range(np.shape(bragg)[0]):
	for j in range(np.shape(bragg)[1]):
		braggs = gdspy.Polygon(bragg[i][j],cond_layer)
		conductor = gdspy.fast_boolean(conductor,braggs, 'or', 
			precision=1e-9, max_points=1000, layer=cond_layer)
		poly_cell.add(braggs)

# FEEDLINE SECTIONS
#############################################################################
# Lower feed sections 
#
l1, l2, l3, arc = lengths(wc,gc,rharc,l1)

# Z1 feedline sections 
xf0al = x0 + no_periods*(mirror_width(w1,g1,rharc) + mirror_width(w2,g2,rharc))
yf0al = y0 
feedline = rs.straight_trench(l1,w1,g1,xf0al,yf0al,orientation='V')

xf1al,yf1al = [coords(xf0al,rharc+wtot),coords(yf0al,l1)]
feedline += rs.halfarc_trench(rharc,w1,g1,xf1al, yf1al,orient='N',npoints=40)

xf2al,yf2al = [coords(xf1al,rharc),coords(yf1al)]
feedline += rs.straight_trench(-l2-l3/8,w1,g1,xf2al,yf2al,orientation='V')

xf3al,yf3al = [coords(xf2al,-2*rharc),coords(yf2al,-l2-l3/8)]
feedline += rs.quarterarc_trench(rharc*2,w1,g1,xf3al, yf3al,orient='SE',npoints=40)

xf4al,yf4al = [coords(xf3al),coords(yf3al,-2*rharc-wtot)]
feedline += rs.straight_trench(-7*l3/8,w1,g1,xf4al,yf4al,orientation='H')

# Z2 feedline sections
xf0bl,yf0bl = [coords(xf4al,-7*l3/8),coords(yf4al)]
feedline += rs.straight_trench(-l1,w2,g2,xf0bl,yf0bl,orientation='H')

xf1bl,yf1bl = [coords(xf0bl,-l1),coords(yf0bl,-rharc)]
feedline += rs.halfarc_trench(rharc,w2,g2,xf1bl, yf1bl,orient='W',npoints=40)

xf2bl,yf2bl = [coords(xf1bl),coords(yf1bl,-rharc-wtot)]
feedline += rs.straight_trench(l2-543,w2,g2,xf2bl,yf2bl,orientation='H')

xf3bl,yf3bl = [coords(xf2bl,l2-543),coords(yf2bl,-rharc)]
feedline += rs.halfarc_trench(rharc,w2,g2,xf3bl, yf3bl,orient='E',npoints=40)

xf4bl,yf4bl = [coords(xf3bl),coords(yf3bl,-rharc-wtot)]
feedline += rs.straight_trench(-l3,w2,g2,xf4bl,yf4bl,orientation='H')

xf5bl,yf5bl = [coords(xf4bl,-l3),coords(yf4bl,-2*rharc)]
feedline += rs.quarterarc_trench(2*rharc,w2,g2,xf5bl,yf5bl,orient='NW',npoints=20)

xf6bl,yf6bl = [coords(xf5bl,-2*rharc-wtot),coords(yf5bl)]
feedline += rs.straight_trench(-300,w2,g2,xf6bl,yf6bl,orientation='V')

# for i in range(0,len(feedline)):
# 	infeed = gdspy.Polygon(feedline[i],2)
# 	# conductor = gdspy.fast_boolean(conductor,outfeed, 'or', 
# 	# 	precision=1e-9, max_points=1000, layer=cond_layer)
# 	poly_cell.add(infeed)

bondl = 150
bondw = 4*bondl

xbond = xf6bl - bondw/2 + g2 + w2/2
ybond = yf6bl - 300 - bondl - 600

x0 = xf6bl
y0 = yf6bl - 300

x02 = x0 + g2 + w2

x1 = xbond
y1 = ybond + bondl

x2 = xbond + bondw - bondl
y2 = ybond + bondl + 300


feed = [rs.rect(bondw,bondl, xbond, ybond)]
feed += [rs.rect(bondl,300,xbond,ybond+bondl)]
feed += [rs.rect(bondl,300,xbond+bondw-bondl,ybond+bondl)]

d1 = [(x0, y0), (x0+g2, y0), (x1+bondl, y2), (x1, y2)]
d2 = [(x02, y0), (x02+g2, y0), (x1+bondw, y2), (x1+bondw-bondl, y2)]
feed += [d1,d2]

for i in range(0,len(feed)):
	outfeed = gdspy.Polygon(feed[i],2)
	# conductor = gdspy.fast_boolean(conductor,outfeed, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(outfeed)


# Z1 feedline sections 
xf0au = xf0al#x0 + no_periods*(mirror_width(w1,g1,rharc) + mirror_width(w2,g2,rharc))
yf0au = y0u 
feedline += rs.straight_trench(-l1,w1,g1,xf0au,yf0au,orientation='V')

xf1au,yf1au = [coords(xf0au,rharc+wtot),coords(yf0au,-l1)]
feedline += rs.halfarc_trench(rharc,w1,g1,xf1au, yf1au,orient='S',npoints=40)

xf2au,yf2au = [coords(xf1au,rharc),coords(yf1au)]
feedline += rs.straight_trench(l2+l3/8,w1,g1,xf2au,yf2au,orientation='V')

xf3au,yf3au = [coords(xf2au,-2*rharc),coords(yf2au,l2+l3/8)]
feedline += rs.quarterarc_trench(rharc*2,w1,g1,xf3au, yf3au,orient='NE',npoints=40)

xf4au,yf4au = [coords(xf3au),coords(yf3au,2*rharc)]
feedline += rs.straight_trench(-7*l3/8,w1,g1,xf4au,yf4au,orientation='H')

# Z2 feedline sections
xf0bu,yf0bu = [coords(xf4au,-7*l3/8),coords(yf4au)]
feedline += rs.straight_trench(-l1,w2,g2,xf0bu,yf0bu,orientation='H')

xf1bu,yf1bu = [coords(xf0bu,-l1),coords(yf0bu,rharc+wtot)]
feedline += rs.halfarc_trench(rharc,w2,g2,xf1bu, yf1bu,orient='W',npoints=40)

xf2bu,yf2bu = [coords(xf1bu),coords(yf1bu,rharc)]
feedline += rs.straight_trench(l2-543,w2,g2,xf2bu,yf2bu,orientation='H')

xf3bu,yf3bu = [coords(xf2bu,l2-543),coords(yf2bu,rharc+wtot)]
feedline += rs.halfarc_trench(rharc,w2,g2,xf3bu, yf3bu,orient='E',npoints=40)

xf4bu,yf4bu = [coords(xf3bu),coords(yf3bu,rharc)]
feedline += rs.straight_trench(-l3,w2,g2,xf4bu,yf4bu,orientation='H')

xf5bu,yf5bu = [coords(xf4bu,-l3),coords(yf4bu,2*rharc+wtot)]
feedline += rs.quarterarc_trench(2*rharc,w2,g2,xf5bu,yf5bu,orient='SW',npoints=20)

xf6bu,yf6bu = [coords(xf5bu,-2*rharc-wtot),coords(yf5bu)]
feedline += rs.straight_trench(300,w2,g2,xf6bu,yf6bu,orientation='V')

for i in range(0,len(feedline)):
	infeed = gdspy.Polygon(feedline[i],2)
	# conductor = gdspy.fast_boolean(conductor,outfeed, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(infeed)

xbond = xf6bu - bondw/2 + ghigh + whigh/2
ybond = yf6bu + 300 + bondl + 600

x0 = xf6bu
y0 = yf6bu + 300

x02 = x0 + g2 + w2

x1 = xbond
y1 = ybond - 2*bondl

x2 = xbond + bondw - bondl
y2 = ybond - 2*bondl 


feed = [rs.rect(bondw,bondl, xbond, ybond)]
feed += [rs.rect(bondl,300,xbond,ybond-2*bondl)]
feed += [rs.rect(bondl,300,xbond+bondw-bondl,ybond-2*bondl)]

d1 = [(x0, y0), (x0+g2, y0), (x1+bondl, y2), (x1, y2)]
d2 = [(x02, y0), (x02+g2, y0), (x1+bondw, y2), (x1+bondw-bondl, y2)]
feed += [d1,d2]

for i in range(0,len(feed)):
	outfeed = gdspy.Polygon(feed[i],2)
	# conductor = gdspy.fast_boolean(conductor,outfeed, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(outfeed)

#############################################################################
# circuit = gdspy.fast_boolean(dots,conductor,'or',
# 	precision=1e-9, max_points=1000, layer=sub_layer)

# poly_cell.add(circuit)

###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
