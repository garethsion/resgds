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
layout_file ='Cavity_test.gds'

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

# Cavity [layer 2]
# I assign coordinates first, and then build geometries accordingly
############################################################################
coords = lambda x,dx=0: x+dx
x0,y0 = [coords(725),coords(sub_y/2-997)]

taper_length = 80
lcav1 = 1000 - taper_length
# lcav1 = lbragg3-taper_length
lcav2 = 1500
lcav3 = 230
lcav4 = 1000
ld = lcav2 - lcav1


cav_xtaper, cav_ytaper = [coords(x0),coords(y0)]
xr = x0 + 2*g1 + w1
taperL = [ (x0,y0), (x0+g1, y0), (x0+gc,y0-taper_length),(x0,y0-taper_length)]
taperR = [ (xr,y0), (xr-g1, y0), (xr-gc,y0-taper_length),(xr,y0-taper_length)]
cav = [taperL,taperR]

cav_x0,cav_y0 = [coords(x0),coords(y0,-lcav1-taper_length)]
cav += rs.straight_trench(lcav1+taper_length,wc,gc, cav_x0, cav_y0, orientation='V')

cav_x1,cav_y1 = [coords(cav_x0,-rharc),coords(cav_y0,)]
cav += rs.halfarc_trench(rharc,wc,gc,cav_x1,cav_y1,orient='S',npoints=40)

cav_x2,cav_y2 = [coords(cav_x1,-rharc-wtot),coords(cav_y1)]
cav += rs.straight_trench(lcav2-ld,wc,gc,cav_x2,cav_y2,orientation='V')

cav_x3,cav_y3 = [coords(cav_x2,-rharc),coords(cav_y2,lcav2-ld)]
cav += rs.halfarc_trench(rharc,wc,gc,cav_x3,cav_y3,orient='N',npoints=40)

cav_x4,cav_y4 = [coords(cav_x3,-rharc-wtot),coords(cav_y3)]
cav += rs.straight_trench(-lcav3,wc,gc,cav_x4,cav_y4,orientation='V')

cav_x5,cav_y5 = [coords(cav_x4,-rharc),coords(cav_y4,-lcav3)]
cav += rs.halfarc_trench(rharc,wc,gc,cav_x5,cav_y5,orient='S',npoints=40)

cav_x6,cav_y6 = [coords(cav_x5,-rharc-wtot),coords(cav_y5)]
cav += rs.straight_trench(lcav4+ld,wc,gc,cav_x6,cav_y6,orientation='V')

cav_x7,cav_y7 = [coords(cav_x6,rharc+wtot),coords(cav_y6,lcav4+ld)]
cav += rs.halfarc_trench(rharc,wc,gc,cav_x7,cav_y7,orient='N',npoints=40)

cav_x8,cav_y8 = [coords(cav_x7,rharc),coords(cav_y7)]
cav += rs.straight_trench(-lcav3,wc,gc,cav_x8,cav_y8,orientation='V')

cav_x9,cav_y9 = [coords(cav_x8,rharc+wtot),coords(cav_y8,-lcav3)]
cav += rs.halfarc_trench(rharc,wc,gc,cav_x9,cav_y9,orient='S',npoints=40)

cav_x10,cav_y10 = [coords(cav_x9,rharc),coords(cav_y9)]
cav += rs.straight_trench(lcav2-ld,wc,gc,cav_x10,cav_y10,orientation='V')

cav_x11,cav_y11 = [coords(cav_x10,rharc+wtot),coords(cav_y10,lcav2-ld)]
cav += rs.halfarc_trench(rharc,wc,gc,cav_x11,cav_y11,orient='N',npoints=40)

cav_x12,cav_y12 = [coords(cav_x11,rharc),coords(cav_y11)]
cav += rs.straight_trench(-lcav1,wc,gc,cav_x12,cav_y12,orientation='V')

cav_x13,cav_y13 = [coords(cav_x12),coords(cav_y12,-lcav1-taper_length)]
taperL = [ (cav_x13,cav_y13), (cav_x13+g1, cav_y13), (cav_x13+gc,cav_y13+taper_length),(cav_x13,cav_y13+taper_length)]
taperR = [ (xr,cav_y13), (xr-g1, cav_y13), (xr-gc,cav_y13+taper_length),(xr,cav_y13+taper_length)]
cav += [taperL,taperR]

for i in range(0,len(cav)):
	cavity = gdspy.Polygon(cav[i],cond_layer)
	# conductor = gdspy.fast_boolean(conductor,cavity, 'or', 
	# 	precision=1e-9, max_points=1000, layer=cond_layer)
	poly_cell.add(cavity)


# # Bragg Mirrors
# ##########################################################################
# no_periods = 4
# # bragg = bragg_mirror(w1,g1,rharc,l1,x0,y0,poly_cell)

# # Vectors to store shifting numbers for making mirrors
# arr_l = np.repeat(np.arange(0,no_periods),2*np.ones(no_periods,dtype=int))
# arr_h = np.append(arr_l[1:],[no_periods], axis=0)

# # MAKE LOWER BRAGG MIRRORS
# #-------------------------
# make_lowZ = lambda i: bragg_mirror(w1,g1,rharc,l1,x0 + arr_h[i]*mirror_width(w1,g1,rharc)
#         + arr_l[i]*mirror_width(w2,g2,rharc), y0, poly_cell)

# make_highZ = lambda i: bragg_mirror(w2,g2,rharc,l2,x0 + arr_h[i]*mirror_width(w1,g1,rharc)
#         + arr_l[i]*mirror_width(w2,g2,rharc), y0, poly_cell)

# bragg = [make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 0]
# bragg += [make_highZ(x) for x in range(len(arr_l)) if x % 2 == 1]

# for i in range(np.shape(bragg)[0]):
# 	for j in range(np.shape(bragg)[1]):
# 		braggs = gdspy.Polygon(bragg[i][j],cond_layer)
# 		conductor = gdspy.fast_boolean(conductor,braggs, 'or', 
# 			precision=1e-9, max_points=1000, layer=cond_layer)
# 		poly_cell.add(braggs)

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


# # MAKE LOWER BRAGG MIRRORS
# #-------------------------
# x0 = x0
# y0 = cav_y13

# make_lowZ = lambda i: rotate_mirror(w1,g1,rharc,l1,x0 + arr_h[i]*mirror_width(w1,g1,rharc)
#         + arr_l[i]*mirror_width(w2,g2,rharc), y0, poly_cell)

# make_highZ = lambda i: rotate_mirror(w2,g2,rharc,l2,x0 + arr_h[i]*mirror_width(w1,g1,rharc)
#         + arr_l[i]*mirror_width(w2,g2,rharc), y0, poly_cell)

# bragg = [make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 0]
# bragg += [make_highZ(x) for x in range(len(arr_l)) if x % 2 == 1]

# for i in range(np.shape(bragg)[0]):
# 	for j in range(np.shape(bragg)[1]):
# 		braggs = gdspy.Polygon(bragg[i][j],cond_layer)
# 		conductor = gdspy.fast_boolean(conductor,braggs, 'or', 
# 			precision=1e-9, max_points=1000, layer=cond_layer)
# 		poly_cell.add(braggs)


# #############################################################################
# circuit = gdspy.fast_boolean(dots,conductor,'or',
# 	precision=1e-9, max_points=1000, layer=sub_layer)

# poly_cell.add(circuit)

###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
