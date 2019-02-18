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
layout_file ='CSTBragg1.gds'

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

# # Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# Substrate coordinate list
sub = rs.rect(sub_x,sub_y,0,0)
substrate = gdspy.Polygon(sub, layer=0)

# Cavity sections
#
coords = lambda x,dx=0: x+dx
xb_strt,yb_strt = [coords(725),coords(sub_y/2)- lext2 - lext3 - 140]
lcav1, lcav2, lcav3 = [1000, 5500, 100]
taper_length = 100

cav_x0,cav_y0 = [coords(xb_strt),coords(yb_strt,-lcav1)] 
cav_cond = [rs.rect(wc,lcav1, cav_x0, cav_y0)]

cav_x1,cav_y1 = [coords(xb_strt,-rlow),coords(yb_strt,-lcav1)]
cav_cond += [rs.halfarc(rlow,wc,cav_x1,cav_y1,orientation='S',npoints=40)]

cav_x2,cav_y2 = [coords(xb_strt,-2*rlow-wc),coords(yb_strt,-lcav1)]
cav_cond += [rs.rect(wc,lcav2,cav_x2,cav_y2)]

cav_x3,cav_y3 = [coords(xb_strt,-rlow),coords(yb_strt,lcav2-lcav1)]
cav_cond += [rs.halfarc(rlow,wc,cav_x3,cav_y3,orientation='N',npoints=40)]

cav_x4,cav_y4 = [coords(xb_strt),coords(cav_y3)]
cav_cond += [rs.rect(wc,-lcav1,cav_x4,cav_y4)]


for i in range(0,len(cav_cond)):
	cavity = gdspy.Polygon(cav_cond[i],1)
	poly_cell.add(cavity)


# Cavity substrate remove
crmw = wc+2*gc

cav_x0r,cav_y0r = [coords(xb_strt,-gc),coords(yb_strt,-lcav1)] 
cav_rm = [rs.rect(crmw,lcav1, cav_x0r, cav_y0r)]

cav_x1r,cav_y1r = [coords(cav_x0r,-rlow+gc),coords(yb_strt,-lcav1)]
cav_rm += [rs.halfarc(rlow-gc,crmw,cav_x1r,cav_y1r,orientation='S',npoints=40)]

cav_x2r,cav_y2r = [coords(xb_strt,-2*rlow-gc-wc),coords(yb_strt,-lcav1)]
cav_rm += [rs.rect(crmw,lcav2,cav_x2r,cav_y2r)]

cav_x3r,cav_y3r = [coords(cav_x0r,-rlow+gc),coords(yb_strt,lcav2-lcav1)]
cav_rm += [rs.halfarc(rlow-gc,crmw,cav_x3r,cav_y3r,orientation='N',npoints=40)]

cav_x4r,cav_y4r = [coords(cav_x0r),coords(cav_y3r)]
cav_rm += [rs.rect(crmw,-lcav1,cav_x4r,cav_y4r)]

for i in range(0,len(cav_rm)):
	remove = gdspy.Polygon(cav_rm[i],2)
	substrate = gdspy.fast_boolean(substrate,remove, 'not', 
		precision=1e-9, max_points=1000, layer=0)


# Bragg Mirror Sections
###########################################################################

# LOWER BRAGG SECTIONS
######################
no_periods = 4
highZ = bragg.BraggCST(whigh, ghigh, lhigh, poly_cell, radius=rhigh, layer=2)
lowZ = bragg.BraggCST(wlow, glow, llow, poly_cell, radius=rlow, layer=2)
rmw = wc+2*gc
rmlZ = bragg.BraggCST(rmw, gc, llow, poly_cell, radius=48.315, layer=2)
rmhZ = bragg.BraggCST(rmw, gc, lhigh, poly_cell, radius=34.095, layer=2)

xlz1,ylz1 = [coords(xb_strt+wc/2-wlow/2),coords(yb_strt)]
lz = [lowZ.mirror(xlz1,ylz1, w_remove=wc, g_remove=gc)]

xhz1,yhz1 = [coords(xlz1-wlow/2-whigh/2+lowZ.mirror_width()),coords(yb_strt)]
hz = [highZ.mirror(xhz1,yhz1, w_remove=wc, g_remove=gc)]

xlz2,ylz2 = [coords(xhz1-whigh/2-wlow/2+highZ.mirror_width()),coords(yb_strt)]
lz += [lowZ.mirror(xlz2,ylz2, w_remove=wc, g_remove=gc)]

xhz2,yhz2 = [coords(xlz2-wlow/2-whigh/2+lowZ.mirror_width()),coords(yb_strt)]
hz += [highZ.mirror(xhz2,yhz2, w_remove=wc, g_remove=gc)]

xlz3,ylz3 = [coords(xhz2-whigh/2-wlow/2+highZ.mirror_width()),coords(yb_strt)]
lz += [lowZ.mirror(xlz3,ylz3, w_remove=wc, g_remove=gc)]

xhz3,yhz3 = [coords(xlz3-wlow/2-whigh/2+lowZ.mirror_width()),coords(yb_strt)]
hz += [highZ.mirror(xhz3,yhz3, w_remove=wc, g_remove=gc)]

xlz4,ylz4 = [coords(xhz3-whigh/2-wlow/2+highZ.mirror_width()),coords(yb_strt)]
lz += [lowZ.mirror(xlz4,ylz4, w_remove=wc, g_remove=gc)]

xhz4,yhz4 = [coords(xlz4-wlow/2-whigh/2+lowZ.mirror_width()),coords(yb_strt)]
hz += [highZ.mirror(xhz4,yhz4, w_remove=wc, g_remove=gc)]

# LOWER BRAGG SECTION REMOVES
#############################

ll1,ll2,ll3,arcl = lowZ.section_lengths(wlow,glow)
lengths_low=[ll1,ll2,ll3,arcl]

lh1,lh2,lh3,arch = highZ.section_lengths(whigh,ghigh)
lengths_high=[lh1,lh2,lh3,arch]

xrm1,yrm1 = [coords(xb_strt,-rmw/2+wc/2),coords(yb_strt)]
rm = [rmlZ.mirror_removes(xrm1,yrm1,lengths_low)]

xrm2,yrm2 = [coords(xrm1,-wlow+lowZ.mirror_width()),coords(yb_strt)]
rm += [rmhZ.mirror_removes(xrm2,yrm2,lengths_high)]

xrm3,yrm3 = [coords(xrm2,-whigh+highZ.mirror_width()),coords(yb_strt)]
rm += [rmlZ.mirror_removes(xrm3,yrm3,lengths_low)]

xrm4,yrm4 = [coords(xrm3,-wlow+lowZ.mirror_width()),coords(yb_strt)]
rm += [rmhZ.mirror_removes(xrm4,yrm4,lengths_high)]

xrm5,yrm5 = [coords(xrm4,-whigh+highZ.mirror_width()),coords(yb_strt)]
rm += [rmlZ.mirror_removes(xrm5,yrm5,lengths_low)]

xrm6,yrm6 = [coords(xrm5,-wlow+lowZ.mirror_width()),coords(yb_strt)]
rm += [rmhZ.mirror_removes(xrm6,yrm6,lengths_high)]

xrm7,yrm7 = [coords(xrm6,-whigh+highZ.mirror_width()),coords(yb_strt)]
rm += [rmlZ.mirror_removes(xrm7,yrm7,lengths_low)]

xrm8,yrm8 = [coords(xrm7,-wlow+lowZ.mirror_width()),coords(yb_strt)]
rm += [rmhZ.mirror_removes(xrm8,yrm8,lengths_high)]

for i in range(0, np.shape(lz)[0]):
	for j in range(0, np.shape(lz)[1]):
		mirror_lz = gdspy.Polygon(lz[i][j],1)
		mirror_hz = gdspy.Polygon(hz[i][j],1)
		poly_cell.add(mirror_lz)
		poly_cell.add(mirror_hz)

for i in range(0, np.shape(rm)[0]):
	for j in range(0, np.shape(rm)[1]):
		mirror_rm = gdspy.Polygon(rm[i][j],2)
		substrate = gdspy.fast_boolean(substrate,mirror_rm, 'not', 
		precision=1e-9, max_points=1000, layer=0)

# UPPER BRAGG SECTIONS
######################

xlz1,ylz1 = [coords(xb_strt+wc/2-wlow/2),coords(cav_y4,-lcav1)]
lz = [lowZ.rotate_mirror(xlz1,ylz1, w_remove=wc, g_remove=gc)]

xhz1,yhz1 = [coords(xlz1-wlow/2-whigh/2+lowZ.mirror_width()),coords(ylz1)]
hz = [highZ.rotate_mirror(xhz1,yhz1, w_remove=wc, g_remove=gc)]

xlz2,ylz2 = [coords(xhz1-whigh/2-wlow/2+highZ.mirror_width()),coords(yhz1)]
lz += [lowZ.rotate_mirror(xlz2,ylz2, w_remove=wc, g_remove=gc)]

xhz2,yhz2 = [coords(xlz2-wlow/2-whigh/2+lowZ.mirror_width()),coords(ylz1)]
hz += [highZ.rotate_mirror(xhz2,yhz2, w_remove=wc, g_remove=gc)]

xlz3,ylz3 = [coords(xhz2-whigh/2-wlow/2+highZ.mirror_width()),coords(yhz1)]
lz += [lowZ.rotate_mirror(xlz3,ylz3, w_remove=wc, g_remove=gc)]

xhz3,yhz3 = [coords(xlz3-wlow/2-whigh/2+lowZ.mirror_width()),coords(ylz1)]
hz += [highZ.rotate_mirror(xhz3,yhz3, w_remove=wc, g_remove=gc)]

xlz4,ylz4 = [coords(xhz3-whigh/2-wlow/2+highZ.mirror_width()),coords(yhz1)]
lz += [lowZ.rotate_mirror(xlz4,ylz4, w_remove=wc, g_remove=gc)]

xhz4,yhz4 = [coords(xlz4-wlow/2-whigh/2+lowZ.mirror_width()),coords(ylz1)]
hz += [highZ.rotate_mirror(xhz4,yhz4, w_remove=wc, g_remove=gc)]

for i in range(0, np.shape(lz)[0]):
	for j in range(0, np.shape(lz)[1]):
		mirror_lz = gdspy.Polygon(lz[i][j],1)
		mirror_hz = gdspy.Polygon(hz[i][j],1)
		poly_cell.add(mirror_lz)
		poly_cell.add(mirror_hz)

# UPPER BRAGG SECTION REMOVES
#############################

xrm1,yrm1 = [coords(xb_strt,-rmw/2+wc/2),coords(ylz1)]
rm = [rmlZ.rotate_mirror_removes(xrm1,yrm1,lengths_low)]

xrm2,yrm2 = [coords(xrm1,-wlow+lowZ.mirror_width()),coords(ylz1)]
rm += [rmhZ.rotate_mirror_removes(xrm2,yrm2,lengths_high)]

xrm3,yrm3 = [coords(xrm2,-whigh+highZ.mirror_width()),coords(ylz1)]
rm += [rmlZ.rotate_mirror_removes(xrm3,yrm3,lengths_low)]

xrm4,yrm4 = [coords(xrm3,-wlow+lowZ.mirror_width()),coords(ylz1)]
rm += [rmhZ.rotate_mirror_removes(xrm4,yrm4,lengths_high)]

xrm5,yrm5 = [coords(xrm4,-whigh+highZ.mirror_width()),coords(ylz1)]
rm += [rmlZ.rotate_mirror_removes(xrm5,yrm5,lengths_low)]

xrm6,yrm6 = [coords(xrm5,-wlow+lowZ.mirror_width()),coords(ylz1)]
rm += [rmhZ.rotate_mirror_removes(xrm6,yrm6,lengths_high)]

xrm7,yrm7 = [coords(xrm6,-whigh+highZ.mirror_width()),coords(ylz1)]
rm += [rmlZ.rotate_mirror_removes(xrm7,yrm7,lengths_low)]

xrm8,yrm8 = [coords(xrm7,-wlow+lowZ.mirror_width()),coords(ylz1)]
rm += [rmhZ.rotate_mirror_removes(xrm8,yrm8,lengths_high)]

for i in range(0, np.shape(rm)[0]):
	for j in range(0, np.shape(rm)[1]):
		mirror_rm = gdspy.Polygon(rm[i][j],2)
		substrate = gdspy.fast_boolean(substrate,mirror_rm, 'not', 
		precision=1e-9, max_points=1000, layer=0)

poly_cell.add(substrate)


###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
