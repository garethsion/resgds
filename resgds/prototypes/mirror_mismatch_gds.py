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
layout_file ='mirror_mismatch.gds'

# Parameters
#__________________________________________________________
sub_x, sub_y = [5000, 5000] # substrate dimensions
wc, gc, lc = [8.11, 17.85, 8108.45] # Cavity width, gap, length
# wlow was 41.81
# whigh was 1
wlow, llow = [39.81, 4051.32]  # Low Z section
whigh, lhigh = [2, 4051.32] # High Z section
glow, ghigh = [.5*(wc + 2*gc - wlow),.5*(wc + 2*gc - whigh)]

rcav, rlow, rhigh = [50, 50, 50]

# Start making resonator geometry
############################################################################

# # Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# Substrate coordinate list
sub = rs.rect(sub_x,sub_y,0,0)
substrate = gdspy.Polygon(sub, layer=0)

coords = lambda x,dx=0: x+dx

# CAVITY SECTION
####################

lcav1, lcav2, arcc = cavlengths(lc, rcav)

xb_strt,yb_strt = [coords(sub_x/2-arcc),coords(sub_y/2)]

cav_x0,cav_y0 = [coords(xb_strt),coords(yb_strt,-lcav1)] 
cav_cond = rs.straight_trench(lcav1,wc,gc, cav_x0, cav_y0, 'V')

cav_x1,cav_y1 = [coords(cav_x0,rcav+wc+2*gc),coords(cav_y0)]
cav_cond += rs.halfarc_trench(rcav,wc,gc,cav_x1,cav_y1,orient='S',npoints=40)

cav_x2,cav_y2 = [coords(cav_x1,rcav),coords(cav_y1)] 
cav_cond += rs.straight_trench(lcav2, wc, gc, cav_x2, cav_y2,'V')

cav_x3,cav_y3 = [coords(cav_x2,rcav+wc+2*gc),coords(cav_y2,lcav2)]
cav_cond += rs.halfarc_trench(rcav,wc,gc,cav_x3,cav_y3,orient='N',npoints=40)

cav_x4,cav_y4 = [coords(cav_x3,rcav),coords(cav_y3)] 
cav_cond += rs.straight_trench(-lcav2, wc, gc, cav_x4, cav_y4, 'V')

cav_x5,cav_y5 = [coords(cav_x4,rcav+wc+2*gc),coords(cav_y4,-lcav2)]
cav_cond += rs.halfarc_trench(rcav,wc,gc,cav_x5,cav_y5,orient='S',npoints=40)

cav_x6,cav_y6 = [coords(cav_x5,rcav),coords(cav_y5)] 
cav_cond += rs.straight_trench(lcav2,wc,gc, cav_x6, cav_y6,'V')

cav_x7,cav_y7 = [coords(cav_x6,rcav+wc+2*gc),coords(cav_y6,lcav2)]
cav_cond += rs.halfarc_trench(rcav,wc,gc,cav_x7,cav_y7,orient='N',npoints=40)

cav_x8,cav_y8 = [coords(cav_x7,rcav),coords(cav_y7)] 
cav_cond += rs.straight_trench(-lcav1,wc,gc, cav_x8, cav_y8,'V')

for i in range(0,len(cav_cond)):
	cavity = gdspy.Polygon(cav_cond[i],1)
	poly_cell.add(cavity)


# LHS MISMATCH SECTIONS
#################################

rhigh = rcav
rlow = rhigh
lh1, lh2, arch = [lcav1, lcav2, arcc]
ll1, ll2, arcl = [lh1, lh2, arch]

# High Impedance
#
mish_x0L,mish_y0L = [coords(cav_x0),coords(cav_y0,lh1)] 
mis_L = rs.straight_trench(lh1,whigh,ghigh, mish_x0L, mish_y0L,'V')

mish_x1L,mish_y1L = [coords(mish_x0L,-rhigh),coords(mish_y0L,lh1)]
mis_L += rs.halfarc_trench(rhigh,whigh,ghigh,mish_x1L,mish_y1L,orient='N',npoints=40)

mish_x2L,mish_y2L = [coords(mish_x1L,-rhigh-whigh-2*ghigh),coords(mish_y1L)] 
mis_L += rs.straight_trench(-lh2,whigh,ghigh, mish_x2L, mish_y2L,'V')

mish_x3L,mish_y3L = [coords(mish_x2L,-rhigh),coords(mish_y2L,-lh2)]
mis_L += rs.halfarc_trench(rhigh,whigh,ghigh,mish_x3L,mish_y3L,orient='S',npoints=40)

mish_x4L,mish_y4L = [coords(mish_x3L,-rhigh-whigh-2*ghigh),coords(mish_y3L)] 
mis_L += rs.straight_trench(lh1,whigh,ghigh, mish_x4L, mish_y4L,'V')

# Low Impedance
#
ll2s = ll1/2
ll3s = ll2s+arcl/2
lt = 2*ll1 + 2*ll2s + ll3s + 3*arcl +  arcl/2 
lr = .5*(lhigh - lt)

misl_x0L,misl_y0L = [coords(mish_x4L),coords(mish_y4L,ll1)] 
mis_L += rs.straight_trench(ll1,wlow,glow, misl_x0L, misl_y0L,'V')

misl_x1L,misl_y1L = [coords(misl_x0L,-rlow),coords(misl_y0L,ll1)]
mis_L += rs.halfarc_trench(rlow,wlow,glow,misl_x1L,misl_y1L,orient='N',npoints=40)

misl_x2L,misl_y2L = [coords(misl_x1L,-rlow-wlow-2*glow),coords(misl_y1L)] 
mis_L += rs.straight_trench(-ll1,wlow,glow, misl_x2L, misl_y2L,'V')

misl_x3L,misl_y3L = [coords(misl_x2L,-rlow),coords(misl_y2L,-ll1)]
mis_L += rs.halfarc_trench(rlow,wlow,glow,misl_x3L,misl_y3L,orient='S',npoints=40)

misl_x4L,misl_y4L = [coords(misl_x3L,-rlow-wlow-2*glow),coords(misl_y3L)] 
mis_L += rs.straight_trench(ll2s+lr,wlow,glow, misl_x4L, misl_y4L,'V')

misl_x5L,misl_y5L = [coords(misl_x4L,-rlow),coords(misl_y4L,ll2s+lr)]
mis_L += rs.halfarc_trench(rlow,wlow,glow,misl_x5L,misl_y5L,orient='N',npoints=40)

misl_x6L,misl_y6L = [coords(misl_x5L,-rlow-wlow-2*glow),coords(misl_y5L)] 
mis_L += rs.straight_trench(-lr-ll2s,wlow,glow, misl_x6L, misl_y6L,'V')

misl_x7L,misl_y7L = [coords(misl_x6L,-rlow),coords(misl_y6L,-lr-ll2s)]
mis_L += rs.quarterarc_trench(rlow,wlow,glow,misl_x7L,misl_y7L,orient='SE',npoints=40)

ll3s = ll2s+arcl/2

misl_x8L,misl_y8L = [coords(misl_x7L,-ll3s),coords(misl_y7L,-rlow-wlow-2*glow)] 
mis_L += rs.straight_trench(ll3s,wlow,glow, misl_x8L, misl_y8L,'H')


for i in range(0,len(mis_L)):
	mis = gdspy.Polygon(mis_L[i],1)
	poly_cell.add(mis)

l = 300
w = 2*l


xoff = 100

x0 = misl_x8L
y0 = misl_y8L + 2*glow+wlow
ycent = y0 - glow - wlow/2

x1 = x0 - 400
y1 = y0

d1 = [(x0,y0), (x0,y0-glow), (x1,ycent+(w/2)-100), (x1,ycent+w/2)]
d2 = [(x0,y0-glow-wlow), (x0,y0-2*glow-wlow), (x1,ycent-w/2), (x1,ycent-(w/2)+100)]

feed = [d1,d2]
l=l/2
feed += [rs.rect(l,w, x1-l, y0-w/2-wlow/2)]

for i in range(0,len(feed)):
	infeed = gdspy.Polygon(feed[i],1)
	poly_cell.add(infeed)

# RHS MISMATCH SECTIONS
#################################

# High Impedance
#

mish_x0R,mish_y0R = [coords(cav_x8),coords(cav_y8,-lh1)] 
mis_R = rs.straight_trench(-lh1,whigh,ghigh, mish_x0R, mish_y0R,'V')

mish_x1R,mish_y1R = [coords(mish_x0R,rhigh+whigh+2*ghigh),coords(mish_y0R,-lh1)]
mis_R += rs.halfarc_trench(rhigh,whigh,ghigh,mish_x1R,mish_y1R,orient='S',npoints=40)

mish_x2R,mish_y2R = [coords(mish_x1R,rhigh),coords(mish_y1R)] 
mis_R += rs.straight_trench(lh2,whigh,ghigh, mish_x2R, mish_y2R,'V')

mish_x3R,mish_y3R = [coords(mish_x2R,rhigh+whigh+2*ghigh),coords(mish_y2R,lh2)]
mis_R += rs.halfarc_trench(rhigh,whigh,ghigh,mish_x3R,mish_y3R,orient='N',npoints=40)

mish_x4R,mish_y4R = [coords(mish_x3R,rhigh),coords(mish_y3R)] 
mis_R += rs.straight_trench(-lh1,whigh,ghigh, mish_x4R, mish_y4R,'V')


# Low Impedance
#

misl_x0R,misl_y0R = [coords(mish_x4R),coords(mish_y4R,-ll1)] 
mis_R += rs.straight_trench(-ll1,wlow,glow, misl_x0R, misl_y0R,'V')

misl_x1R,misl_y1R = [coords(misl_x0R,rlow+2*glow+wlow),coords(misl_y0R,-ll1)]
mis_R += rs.halfarc_trench(rlow,wlow,glow,misl_x1R,misl_y1R,orient='S',npoints=40)

misl_x2R,misl_y2R = [coords(misl_x1R,rlow),coords(misl_y1R)] 
mis_R += rs.straight_trench(ll1,wlow,glow, misl_x2R, misl_y2R,'V')

misl_x3R,misl_y3R = [coords(misl_x2R,rlow+2*glow+wlow),coords(misl_y2R,ll1)]
mis_R += rs.halfarc_trench(rlow,wlow,glow,misl_x3R,misl_y3R,orient='N',npoints=40)

misl_x4R,misl_y4R = [coords(misl_x3R,rlow),coords(misl_y3R)] 
mis_R += rs.straight_trench(-ll2s-lr,wlow,glow, misl_x4R, misl_y4R,'V')

misl_x5R,misl_y5R = [coords(misl_x4R,rlow+2*glow+wlow),coords(misl_y4R,-ll2s-lr)]
mis_R += rs.halfarc_trench(rlow,wlow,glow,misl_x5R,misl_y5R,orient='S',npoints=40)

misl_x6R,misl_y6R = [coords(misl_x5R,rlow),coords(misl_y5R)] 
mis_R += rs.straight_trench(lr+ll2s,wlow,glow, misl_x6R, misl_y6R,'V')

misl_x7R,misl_y7R = [coords(misl_x6R,rlow+2*glow+wlow),coords(misl_y6R,lr+ll2s)]
mis_R += rs.quarterarc_trench(rlow,wlow,glow,misl_x7R,misl_y7R,orient='NW',npoints=40)

misl_x8R,misl_y8R = [coords(misl_x7R,ll3s),coords(misl_y7R,rlow)] 
mis_R += rs.straight_trench(-ll3s,wlow,glow, misl_x8R, misl_y8R,'H')


for i in range(0,len(mis_R)):
	mis = gdspy.Polygon(mis_R[i],1)
	poly_cell.add(mis)

x0 = misl_x8R
y0 = misl_y8R + 2*glow+wlow
ycent = y0 - glow - wlow/2

x1 = x0 + 400
y1 = y0

d1 = [(x0,y0), (x0,y0-glow), (x1,ycent+(w/2)-100), (x1,ycent+w/2)]
d2 = [(x0,y0-glow-wlow), (x0,y0-2*glow-wlow), (x1,ycent-w/2), (x1,ycent-(w/2)+100)]

feed = [d1,d2]

feed += [rs.rect(l,w, x1, y0-w/2-wlow/2)]

for i in range(0,len(feed)):
	infeed = gdspy.Polygon(feed[i],1)
	poly_cell.add(infeed)

poly_cell.add(substrate)


###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
