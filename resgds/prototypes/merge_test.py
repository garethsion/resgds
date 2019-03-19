#!/usr/bin/env python
import os
from resgds import *
import bragg
from interface import Interface
import gdspy # gds library
import numpy as np
#from subprocess import call # Use to call kaloput_viewer bash script
#import psutil # Use to check if klayout is running already

def cavlengths(lt, rad):

    arc = .5 * (2*np.pi*rad) 

    l_remain = lt - 4*arc
    lr = l_remain/4

    l1 = lr/2
    l2 = lr

    # lt = 2*l1 + 3*l2 + 4*arc
    # print(lt)
    return l1, l2, arc

def quarterlengths(lt, rad):

    arc = .5 * (2*np.pi*rad) 

    l_remain = lt - 4*arc
    lr = l_remain/4

    l1 = lr/2
    l2 = lr

    # lt = 2*l1 + 3*l2 + 4*arc
    # print(lt)
    return l1, l2, arc

def mismatch(xstart, ystart, w1, w2, l1, l2, rad):

	x0,y0 = [coords(xstart,w1/2-w2/2),coords(ystart,l1)] 
	mis = [rs.rect(w2,l1, x0, y0)]

	x1,y1 = [coords(x0,-rad),coords(y0,l1)]
	mis += [rs.halfarc(rad,w2,x1,y1,orientation='N',npoints=40)]

	x2,y2 = [coords(x1,-rad-w2),coords(y1)] 
	mis += [rs.rect(w2,-l2, x2, y2)]

	x3,y3 = [coords(x2,-rad),coords(y2,-l2)]
	mis += [rs.halfarc(rad,w2,x3,y3,orientation='S',npoints=40)]

	x4,y4 = [coords(x3,-rad-w2),coords(y3)] 
	mis += [rs.rect(w2,l1, x4, y4)]



	return mis,x4,y4



# Layout filename
layout_file ='fab_files/merged_test.gds'

# Parameters
#__________________________________________________________
sub_x, sub_y = [5000, 5000] # substrate dimensions
wc, gc, lc = [8.11, 17.85, 8108.45] # Cavity width, gap, length
# wlow was 41.81
# whigh was 1
wlow = wc
glow = gc
# wlow, llow = [39.81, 4051.32]  # Low Z section
whigh, lhigh = [2, 4051.32] # High Z section

rcav, rlow, rhigh = [50, 50, 50]

wrhead_xoff = -1670
wrhead_yoff = 970

# layers 
sub_layer = 0
dot_layer = 1
cond_layer = 2
rem_layer = 3

# Start making resonator geometry
############################################################################

# # Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# Substrate coordinate list
sub = rs.rect(sub_x,sub_y,wrhead_xoff,wrhead_yoff)
substrate = gdspy.Polygon(sub, layer=sub_layer)

# Dots
layout = LayoutComponents(poly_cell, sub_x, sub_y,layer=dot_layer)
dots = layout.antidot_array(wrhead_xoff,wrhead_yoff,10,30,0)

coords = lambda x,dx=0: x+dx
lcav1, lcav2, arcc = cavlengths(lc, rcav)
# xb_strt,yb_strt = [coords(sub_x/2-arcc),coords(sub_y/2)]
xb_strt,yb_strt = [coords(sub_x/2,wrhead_xoff),coords(sub_y/4+307.5,wrhead_yoff)]


# Low Impedance
#
lh1, lh2, arch = [lcav1, lcav2, arcc]
ll1, ll2, arcl = [lh1, lh2, arch]

ll2s = ll1/2
ll3s = ll2s+arcl/2
lt = 2*ll1 + 2*ll2s + ll3s + 3*arcl +  arcl/2 
lr = .5*(lhigh - lt)

cent = 35 # offset for centering

misl_x0L,misl_y0L = [coords(xb_strt),coords(yb_strt,ll1)] 
mis_L = rs.straight_trench(ll1,wlow,glow, misl_x0L, misl_y0L,'V')

misl_x1L,misl_y1L = [coords(misl_x0L,-rlow),coords(misl_y0L,ll1)]
mis_L += rs.halfarc_trench(rlow,wlow,glow,misl_x1L,misl_y1L,orient='N',npoints=40)

misl_x2L,misl_y2L = [coords(misl_x1L,-rlow-wlow-2*glow),coords(misl_y1L)] 
mis_L += rs.straight_trench(-ll1,wlow,glow, misl_x2L, misl_y2L,'V')

misl_x3L,misl_y3L = [coords(misl_x2L,-rlow),coords(misl_y2L,-ll1)]
mis_L += rs.halfarc_trench(rlow,wlow,glow,misl_x3L,misl_y3L,orient='S',npoints=40)

misl_x4L,misl_y4L = [coords(misl_x3L,-rlow-wlow-2*glow),coords(misl_y3L)] 
mis_L += rs.straight_trench(ll2s+lr+cent,wlow,glow, misl_x4L, misl_y4L,'V')

misl_x5L,misl_y5L = [coords(misl_x4L,-rlow),coords(misl_y4L,ll2s+lr+cent)]
mis_L += rs.halfarc_trench(rlow,wlow,glow,misl_x5L,misl_y5L,orient='N',npoints=40)

misl_x6L,misl_y6L = [coords(misl_x5L,-rlow-wlow-2*glow),coords(misl_y5L)] 
mis_L += rs.straight_trench(-lr-ll2s+cent,wlow,glow, misl_x6L, misl_y6L,'V')

misl_x7L,misl_y7L = [coords(misl_x6L,-rlow),coords(misl_y6L,-lr-ll2s+cent)]
mis_L += rs.quarterarc_trench(rlow,wlow,glow,misl_x7L,misl_y7L,orient='SE',npoints=40)

ll3s = ll2s+arcl/2

misl_x8L,misl_y8L = [coords(misl_x7L,-ll3s),coords(misl_y7L,-rlow-wlow-2*glow)] 
mis_L += rs.straight_trench(ll3s,wlow,glow, misl_x8L, misl_y8L,'H')

gap = 5
lcapin = 65

misl_x9L,misl_y9L = [coords(misl_x8L,-gap-lcapin),coords(misl_y7L,-rlow-wlow-2*glow)] 
mis_L += rs.straight_trench(lcapin,wlow,glow, misl_x9L, misl_y9L,'H')

misl_x10L,misl_y10L = [coords(misl_x9L,lcapin),coords(misl_y9L)] 
mis_L += [rs.rect(gap,wlow+2*glow, misl_x10L, misl_y10L)]

conductor = []

for i in range(0,len(mis_L)):
	mis = gdspy.Polygon(mis_L[i],cond_layer)
	conductor = gdspy.fast_boolean(conductor,mis, 'or', 
		precision=1e-9, max_points=1000, layer=cond_layer)
poly_cell.add(conductor)
	# poly_cell.add(mis)




###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
