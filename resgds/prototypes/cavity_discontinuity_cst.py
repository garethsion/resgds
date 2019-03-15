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
layout_file ='CSTBragg1.gds'

# Parameters
#__________________________________________________________
sub_x, sub_y = [5000, 5000] # substrate dimensions
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


# Mismatch section
gmis = 500
wmis = 1.4




coords = lambda x,dx=0: x+dx

rcav = 50
lcav1, lcav2, arcc = cavlengths(lc, rcav)

xb_strt,yb_strt = [coords(sub_x/2-arcc),coords(sub_y/2)]

cav_x0,cav_y0 = [coords(xb_strt),coords(yb_strt,-lcav1)] 
cav_cond = [rs.rect(wc,lcav1, cav_x0, cav_y0)]

cav_x1,cav_y1 = [coords(cav_x0,rcav+wc),coords(cav_y0)]
cav_cond += [rs.halfarc(rcav,wc,cav_x1,cav_y1,orientation='S',npoints=40)]

cav_x2,cav_y2 = [coords(cav_x1,rcav),coords(cav_y1)] 
cav_cond += [rs.rect(wc,lcav2, cav_x2, cav_y2)]

cav_x3,cav_y3 = [coords(cav_x2,rcav+wc),coords(cav_y2,lcav2)]
cav_cond += [rs.halfarc(rcav,wc,cav_x3,cav_y3,orientation='N',npoints=40)]

cav_x4,cav_y4 = [coords(cav_x3,rcav),coords(cav_y3)] 
cav_cond += [rs.rect(wc,-lcav2, cav_x4, cav_y4)]

cav_x5,cav_y5 = [coords(cav_x4,rcav+wc),coords(cav_y4,-lcav2)]
cav_cond += [rs.halfarc(rcav,wc,cav_x5,cav_y5,orientation='S',npoints=40)]

cav_x6,cav_y6 = [coords(cav_x5,rcav),coords(cav_y5)] 
cav_cond += [rs.rect(wc,lcav2, cav_x6, cav_y6)]

cav_x7,cav_y7 = [coords(cav_x6,rcav+wc),coords(cav_y6,lcav2)]
cav_cond += [rs.halfarc(rcav,wc,cav_x7,cav_y7,orientation='N',npoints=40)]

cav_x8,cav_y8 = [coords(cav_x7,rcav),coords(cav_y7)] 
cav_cond += [rs.rect(wc,-lcav1, cav_x8, cav_y8)]


for i in range(0,len(cav_cond)):
	cavity = gdspy.Polygon(cav_cond[i],1)
	poly_cell.add(cavity)


# Mismatch sections
rhigh = rcav
rlow = rhigh
# lh1, lh2, arch = quarterlengths(lc/2, rhigh)
lh1, lh2, arch = [lcav1, lcav2, arcc]
ll1, ll2, arcl = [lh1, lh2, arch]

# mis_L,mx,my = mismatch(cav_x0, cav_y0, wc, whigh, lh1, lh2, rhigh)
# mis_L2,mx2,my2 = mismatch(mx, my, whigh, wlow, ll1, ll2, rlow)
# mis_L += mis_L2


# mis_R,mx,my = mismatch(cav_x8, cav_y8-lh1, wc, whigh, lh1, lh2, rhigh)

mish_x0L,mish_y0L = [coords(cav_x0,wc/2-whigh/2),coords(cav_y0,lh1)] 
mis_L = [rs.rect(whigh,lh1, mish_x0L, mish_y0L)]

mish_x1L,mish_y1L = [coords(mish_x0L,-rhigh),coords(mish_y0L,lh1)]
mis_L += [rs.halfarc(rhigh,whigh,mish_x1L,mish_y1L,orientation='N',npoints=40)]

mish_x2L,mish_y2L = [coords(mish_x1L,-rhigh-whigh),coords(mish_y1L)] 
mis_L += [rs.rect(whigh,-lh2, mish_x2L, mish_y2L)]

mish_x3L,mish_y3L = [coords(mish_x2L,-rhigh),coords(mish_y2L,-lh2)]
mis_L += [rs.halfarc(rhigh,whigh,mish_x3L,mish_y3L,orientation='S',npoints=40)]

mish_x4L,mish_y4L = [coords(mish_x3L,-rhigh-whigh),coords(mish_y3L)] 
mis_L += [rs.rect(whigh,lh1, mish_x4L, mish_y4L)]


misl_x0L,misl_y0L = [coords(mish_x4L,whigh/2-wlow/2),coords(mish_y4L,ll1)] 
mis_L += [rs.rect(wlow,ll1, misl_x0L, misl_y0L)]

misl_x1L,misl_y1L = [coords(misl_x0L,-rlow),coords(misl_y0L,ll1)]
mis_L += [rs.halfarc(rlow,wlow,misl_x1L,misl_y1L,orientation='N',npoints=40)]

misl_x2L,misl_y2L = [coords(misl_x1L,-rlow-wlow),coords(misl_y1L)] 
mis_L += [rs.rect(wlow,-ll2, misl_x2L, misl_y2L)]

misl_x3L,misl_y3L = [coords(misl_x2L,-rlow),coords(misl_y2L,-ll2)]
mis_L += [rs.halfarc(rlow,wlow,misl_x3L,misl_y3L,orientation='S',npoints=40)]

misl_x4L,misl_y4L = [coords(misl_x3L,-rlow-wlow),coords(misl_y3L)] 
mis_L += [rs.rect(wlow,ll1, misl_x4L, misl_y4L)]


mish_x0R,mish_y0R = [coords(cav_x8,wc/2-whigh/2),coords(cav_y8,-lh1)] 
mis_R = [rs.rect(whigh,-lh1, mish_x0R, mish_y0R)]

mish_x1R,mish_y1R = [coords(mish_x0R,rhigh+whigh),coords(mish_y0R,-lh1)]
mis_R += [rs.halfarc(rhigh,whigh,mish_x1R,mish_y1R,orientation='S',npoints=40)]

mish_x2R,mish_y2R = [coords(mish_x1R,rhigh),coords(mish_y1R)] 
mis_R += [rs.rect(whigh,lh2, mish_x2R, mish_y2R)]

mish_x3R,mish_y3R = [coords(mish_x2R,rhigh+whigh),coords(mish_y2R,lh2)]
mis_R += [rs.halfarc(rhigh,whigh,mish_x3R,mish_y3R,orientation='N',npoints=40)]

mish_x4R,mish_y4R = [coords(mish_x3R,rhigh),coords(mish_y3R)] 
mis_R += [rs.rect(whigh,-lh1, mish_x4R, mish_y4R)]


misl_x0R,misl_y0R = [coords(mish_x4R,-wlow/2+whigh/2),coords(mish_y4R,-ll1)] 
mis_R += [rs.rect(wlow,-ll1, misl_x0R, misl_y0R)]

misl_x1R,misl_y1R = [coords(misl_x0R,rlow+wlow),coords(misl_y0R,-ll1)]
mis_R += [rs.halfarc(rlow,wlow,misl_x1R,misl_y1R,orientation='S',npoints=40)]

misl_x2R,misl_y2R = [coords(misl_x1R,rlow),coords(misl_y1R)] 
mis_R += [rs.rect(wlow,ll2, misl_x2R, misl_y2R)]

misl_x3R,misl_y3R = [coords(misl_x2R,rlow+wlow),coords(misl_y2R,ll2)]
mis_R += [rs.halfarc(rlow,wlow,misl_x3R,misl_y3R,orientation='N',npoints=40)]

misl_x4R,misl_y4R = [coords(misl_x3R,rlow),coords(misl_y3R)] 
mis_R += [rs.rect(wlow,-ll1, misl_x4R, misl_y4R)]

for i in range(0,len(mis_L)):
	mis = gdspy.Polygon(mis_L[i],1)
	poly_cell.add(mis)

for i in range(0,len(mis_R)):
	mis = gdspy.Polygon(mis_R[i],1)
	poly_cell.add(mis)

# for i in range(0,len(mis_R)):
# 	mis = gdspy.Polygon(mis_R[i],1)
# 	poly_cell.add(mis)

# # Cavity substrate remove
# crmw = wc+2*gc

# cav_x0r,cav_y0r = [coords(xb_strt,-gc),coords(yb_strt,-lcav1)] 
# cav_rm = [rs.rect(crmw,lcav1, cav_x0r, cav_y0r)]

# cav_x1r,cav_y1r = [coords(cav_x0r,-rlow+gc),coords(yb_strt,-lcav1)]
# cav_rm += [rs.halfarc(rlow-gc,crmw,cav_x1r,cav_y1r,orientation='S',npoints=40)]

# cav_x2r,cav_y2r = [coords(xb_strt,-2*rlow-gc-wc),coords(yb_strt,-lcav1)]
# cav_rm += [rs.rect(crmw,lcav2,cav_x2r,cav_y2r)]

# cav_x3r,cav_y3r = [coords(cav_x0r,-rlow+gc),coords(yb_strt,lcav2-lcav1)]
# cav_rm += [rs.halfarc(rlow-gc,crmw,cav_x3r,cav_y3r,orientation='N',npoints=40)]

# cav_x4r,cav_y4r = [coords(cav_x0r),coords(cav_y3r)]
# cav_rm += [rs.rect(crmw,-lcav1,cav_x4r,cav_y4r)]

# for i in range(0,len(cav_rm)):
# 	remove = gdspy.Polygon(cav_rm[i],2)
# 	substrate = gdspy.fast_boolean(substrate,remove, 'not', 
# 		precision=1e-9, max_points=1000, layer=0)

poly_cell.add(substrate)


###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
