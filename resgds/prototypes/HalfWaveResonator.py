#!/usr/bin/env python
import os
from resgds import *
import bragg
from interface import Interface
import gdspy # gds library
import numpy as np
import pandas as pd
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


# df = pd.read_table('write_offsets.txt',sep=',',names=['x','y'])

wrhead_xoff = 0#df['x'].values[0]
wrhead_yoff = 0#df['y'].values[0]

# print('wr_xoff = ', wrhead_xoff)
# print('wr_yoff = ', wrhead_yoff)

# Layout filename
layout_file ='fab_files/discontinuity_xoff='+str(wrhead_yoff)+'_yoff='+str(wrhead_yoff)+'.gds'

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
mis_L += rs.straight_trench(ll2s+lr+cent+ll3s/3,wlow,glow, misl_x4L, misl_y4L,'V')

misl_x5L,misl_y5L = [coords(misl_x4L,-rlow),coords(misl_y4L,ll2s+lr+cent+ll3s/3)]
mis_L += rs.halfarc_trench(rlow,wlow,glow,misl_x5L,misl_y5L,orient='N',npoints=40)

misl_x6L,misl_y6L = [coords(misl_x5L,-rlow-wlow-2*glow),coords(misl_y5L)] 
mis_L += rs.straight_trench(-lr-ll2s+cent-ll3s/3,wlow,glow, misl_x6L, misl_y6L,'V')

misl_x7L,misl_y7L = [coords(misl_x6L,-rlow),coords(misl_y6L,-lr-ll2s+cent-ll3s/3)]
mis_L += rs.quarterarc_trench(rlow,wlow,glow,misl_x7L,misl_y7L,orient='SE',npoints=40)

misl_x8L,misl_y8L = [coords(misl_x7L,-ll3s/3),coords(misl_y7L,-rlow-wlow-2*glow)] 
mis_L += rs.straight_trench(ll3s/3,wlow,glow, misl_x8L, misl_y8L,'H')

gap = 30
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
	# poly_cell.add(mis)
	
# Low Z removes
rm_width = 4*wc + 2*gc
arcrad = .5*(2*rlow - gc - wc)

misl_x0Lr,misl_y0Lr = [coords(xb_strt,-rm_width/2+wlow/2+glow),coords(yb_strt,ll1)] 
mis_Lr = [rs.rect(rm_width,ll1,misl_x0Lr, misl_y0Lr)]

# print(misl_x0L-2*rlow-glow-wlow/2-rm_width/2)

misl_x1Lr,misl_y1Lr = [coords(misl_x0L,-2*rlow-glow-wlow/2-rm_width/2),coords(misl_y0Lr)] 
mis_Lr += [rs.rect(rm_width,ll1, misl_x1Lr, misl_y1Lr)]

rad = .5*(misl_x0Lr - misl_x1Lr - rm_width)

misl_x2Lr,misl_y2Lr = [coords(misl_x1Lr,rad+rm_width),coords(misl_y0Lr,ll1)]
mis_Lr += [rs.halfarc(rad,rm_width,misl_x2Lr,misl_y2Lr,orientation='N',npoints=40)]

misl_x3Lr,misl_y3Lr = [coords(misl_x1Lr,-rad),coords(misl_y1Lr)]
mis_Lr += [rs.halfarc(rad,rm_width,misl_x3Lr,misl_y3Lr,orientation='S',npoints=40)]

misl_x4Lr,misl_y4Lr = [coords(misl_x3Lr,-rad-rm_width),coords(misl_y3Lr)] 
mis_Lr += [rs.rect(rm_width,ll2s+lr+cent+ll3s/3, misl_x4Lr, misl_y4Lr)]

misl_x5Lr,misl_y5Lr = [coords(misl_x4Lr,-rad),coords(misl_y4Lr,ll2s+lr+cent+ll3s/3)]
mis_Lr += [rs.halfarc(rad,rm_width,misl_x5Lr,misl_y5Lr,orientation='N',npoints=40)]

misl_x6Lr,misl_y6Lr = [coords(misl_x5Lr,-rad-rm_width),coords(misl_y5Lr)] 
mis_Lr += [rs.rect(rm_width,-lr-ll2s+cent-ll3s/3, misl_x6Lr, misl_y6Lr)]

misl_x7Lr,misl_y7Lr = [coords(misl_x6Lr,-rad),coords(misl_y6Lr,-lr-ll2s+cent-ll3s/3)]
mis_Lr += [rs.quarterarc(rad,rm_width,misl_x7Lr,misl_y7Lr,orientation='SE',npoints=40)]

misl_x8Lr,misl_y8Lr = [coords(misl_x7Lr,-ll3s/3-gap-lcapin),coords(misl_y7Lr,-rad-rm_width)] 
mis_Lr += [rs.rect(ll3s/3+gap+lcapin,rm_width, misl_x8Lr, misl_y8Lr)]

for i in range(0,len(mis_Lr)):
	misr = gdspy.Polygon(mis_Lr[i],rem_layer)
	# poly_cell.add(misr)
	dots = gdspy.fast_boolean(dots,misr, 'not', 
		precision=1e-9, max_points=1000, layer=dot_layer)

l = 300
w = 2*l

x0 = misl_x9L
y0 = misl_y9L+2*glow+wlow
ycent = y0 - glow - wlow/2

x1 = x0 - 400
y1 = y0
yoff = 100

d1 = [(x0,y0), (x0,y0-glow), (x1,ycent+(w/2)-yoff), (x1,ycent+w/2)]
d2 = [(x0,y0-glow-wlow), (x0,y0-2*glow-wlow), (x1,ycent-w/2), (x1,ycent-(w/2)+yoff)]

feed = [d1,d2]
l=l/2
feed += [rs.rect(l,w, x1-l, ycent-w/2)]

for i in range(0,len(feed)):
	infeed = gdspy.Polygon(feed[i],cond_layer)
	conductor = gdspy.fast_boolean(conductor,infeed, 'or', 
		precision=1e-9, max_points=1000, layer=cond_layer)

# Feed removes
#

x0r = misl_x8Lr
y0r = misl_y8Lr + rm_width
ycentr = y0r - rm_width/2

x1r = x0r-400
y1r = y0r-800

d1r = [(x0r,y0r), (x0r,y0r-rm_width), (x1r,ycentr-400), (x1r,ycentr+400)]

feedr = [d1r]
l = 200
w = 800

feedr += [rs.rect(l,w, x1r-l, ycentr-400)]

for i in range(0,len(feedr)):
	infeedr = gdspy.Polygon(feedr[i],rem_layer)
	# poly_cell.add(infeedr)
	dots = gdspy.fast_boolean(dots,infeedr, 'not', 
		precision=1e-9, max_points=1000, layer=dot_layer)



misl_x0R,misl_y0R = [coords(xb_strt),coords(yb_strt,ll1)] 
mis_R = rs.straight_trench(-ll1,wlow,glow, misl_x0R, misl_y0R,'V')

misl_x1R,misl_y1R = [coords(misl_x0R,rlow+2*glow+wlow),coords(misl_y0R,-ll1)]
mis_R += rs.halfarc_trench(rlow,wlow,glow,misl_x1R,misl_y1R,orient='S',npoints=40)

misl_x2R,misl_y2R = [coords(misl_x1R,rlow),coords(misl_y1R)] 
mis_R += rs.straight_trench(ll1,wlow,glow, misl_x2R, misl_y2R,'V')

misl_x3R,misl_y3R = [coords(misl_x2R,rlow+2*glow+wlow),coords(misl_y2R,ll1)]
mis_R += rs.halfarc_trench(rlow,wlow,glow,misl_x3R,misl_y3R,orient='N',npoints=40)

misl_x4R,misl_y4R = [coords(misl_x3R,rlow),coords(misl_y3R)] 
mis_R += rs.straight_trench(-ll2s-lr-cent-ll3s/3,wlow,glow, misl_x4R, misl_y4R,'V')

misl_x5R,misl_y5R = [coords(misl_x4R,rlow+2*glow+wlow),coords(misl_y4R,-ll2s-lr-cent-ll3s/3)]
mis_R += rs.halfarc_trench(rlow,wlow,glow,misl_x5R,misl_y5R,orient='S',npoints=40)

misl_x6R,misl_y6R = [coords(misl_x5R,rlow),coords(misl_y5R)] 
mis_R += rs.straight_trench(lr+ll2s-cent+ll3s/3,wlow,glow, misl_x6R, misl_y6R,'V')

misl_x7R,misl_y7R = [coords(misl_x6R,rlow+2*glow+wlow),coords(misl_y6R,lr+ll2s-cent+ll3s/3)]
mis_R += rs.quarterarc_trench(rlow,wlow,glow,misl_x7R,misl_y7R,orient='NW',npoints=40)

misl_x8R,misl_y8R = [coords(misl_x7R,ll3s/3),coords(misl_y7R,rlow)] 
mis_R += rs.straight_trench(-ll3s/3,wlow,glow, misl_x8R, misl_y8R,'H')

misl_x9R,misl_y9R = [coords(misl_x8R+gap+lcapin),coords(misl_y7R,rlow)] 
mis_R += rs.straight_trench(-lcapin,wlow,glow, misl_x9R, misl_y9R,'H')

misl_x10R,misl_y10R = [coords(misl_x9R,-lcapin-gap),coords(misl_y9R)] 
mis_R += [rs.rect(gap,wlow+2*glow, misl_x10R, misl_y10R)]


for i in range(0,len(mis_R)):
	mis = gdspy.Polygon(mis_R[i],cond_layer)
	conductor = gdspy.fast_boolean(conductor,mis, 'or', 
		precision=1e-9, max_points=1000, layer=cond_layer)
	# poly_cell.add(mis)

misl_x0Rr,misl_y0Rr = [coords(misl_x0Lr),coords(yb_strt,ll1)] 
mis_Rr = [rs.rect(rm_width,-ll1,misl_x0Rr, misl_y0Rr)]

misl_x1Rr,misl_y1Rr = [coords(misl_x0Rr,rad+rm_width),coords(misl_y0Rr,-ll1)]
mis_Rr += [rs.halfarc(rad,rm_width,misl_x1Rr,misl_y1Rr,orientation='S',npoints=40)]

misl_x2Rr,misl_y2Rr = [coords(misl_x1Rr,rad),coords(misl_y1Rr)] 
mis_Rr += [rs.rect(rm_width,ll1, misl_x2Rr, misl_y2Rr)]

misl_x3Rr,misl_y3Rr = [coords(misl_x2Rr,rad+rm_width),coords(misl_y2Rr,ll1)]
mis_Rr += [rs.halfarc(rad,rm_width,misl_x3Rr,misl_y3Rr,orientation='N',npoints=40)]

misl_x4Rr,misl_y4Rr = [coords(misl_x3Rr,rad),coords(misl_y3Rr)] 
mis_Rr += [rs.rect(rm_width,-ll2s-lr-cent-ll3s/3, misl_x4Rr, misl_y4Rr)]

misl_x5Rr,misl_y5Rr = [coords(misl_x4Rr,rad+rm_width),coords(misl_y4Rr,-ll2s-lr-cent-ll3s/3)]
mis_Rr += [rs.halfarc(rad,rm_width,misl_x5Rr,misl_y5Rr,orientation='S',npoints=40)]

misl_x6Rr,misl_y6Rr = [coords(misl_x5Rr,rad),coords(misl_y5Rr)] 
mis_Rr += [rs.rect(rm_width,lr+ll2s-cent+ll3s/3, misl_x6Rr, misl_y6Rr)]

misl_x7Rr,misl_y7Rr = [coords(misl_x6Rr,rad+rm_width),coords(misl_y6Rr,lr+ll2s-cent+ll3s/3)]
mis_Rr += [rs.quarterarc(rad,rm_width,misl_x7Rr,misl_y7Rr,orientation='NW',npoints=40)]

misl_x8Rr,misl_y8Rr = [coords(misl_x7Rr,ll3s/3+lcapin+gap),coords(misl_y7Rr,rad)] 
mis_Rr += [rs.rect(-ll3s/3-lcapin-gap,rm_width, misl_x8Rr, misl_y8Rr)]

for i in range(0,len(mis_Rr)):
	misr = gdspy.Polygon(mis_Rr[i],rem_layer)
	# poly_cell.add(misr)
	dots = gdspy.fast_boolean(dots,misr, 'not', 
		precision=1e-9, max_points=1000, layer=dot_layer)

l = 300
w = 2*l

x0 = misl_x9R
y0 = misl_y9R + 2*glow+wlow
ycent = y0 - glow - wlow/2

x1 = x0 + 400
y1 = y0

d1 = [(x0,y0), (x0,y0-glow), (x1,ycent+(w/2)-yoff), (x1,ycent+w/2)]
d2 = [(x0,y0-glow-wlow), (x0,y0-2*glow-wlow), (x1,ycent-w/2), (x1,ycent-(w/2)+yoff)]

feed = [d1,d2]
l=l/2
feed += [rs.rect(l,w, x1, ycent-w/2)]

for i in range(0,len(feed)):
	outfeed = gdspy.Polygon(feed[i],cond_layer)
	conductor = gdspy.fast_boolean(conductor,outfeed, 'or', 
		precision=1e-9, max_points=1000, layer=cond_layer)
	# poly_cell.add(outfeed)

# Feed removes
#

x0r = misl_x8Rr
y0r = misl_y8Rr + rm_width
ycentr = y0r - rm_width/2

x1r = x0r+400
y1r = y0r+800

d1r = [(x0r,y0r), (x0r,y0r-rm_width), (x1r,ycentr-400), (x1r,ycentr+400)]

feedr = [d1r]
l = 200
w = 800

feedr += [rs.rect(l,w, x1r, ycentr-400)]

for i in range(0,len(feedr)):
	infeedr = gdspy.Polygon(feedr[i],rem_layer)
	# poly_cell.add(infeedr)
	dots = gdspy.fast_boolean(dots,infeedr, 'not', 
		precision=1e-9, max_points=1000, layer=dot_layer)


circuit = gdspy.fast_boolean(dots,conductor,'or',
	precision=1e-9, max_points=1000, layer=sub_layer)

# poly_cell.add(dots)
# poly_cell.add(conductor)
poly_cell.add(circuit)



###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
