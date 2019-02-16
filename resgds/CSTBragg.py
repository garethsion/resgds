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


# Bragg Mirror Sections [layer 2]
###########################################################################
no_periods = 4
highZ = bragg.BraggCST(whigh, ghigh, lhigh, poly_cell, radius=rhigh, layer=2)
bragg = highZ.mirror(xb_strt+wc/2-whigh/2,yb_strt)

for i in range(0,len(bragg)):
	mirror = gdspy.Polygon(bragg[i],3)
	poly_cell.add(mirror)


for i in range(0,len(cav_rm)):
	remove = gdspy.Polygon(cav_rm[i],2)
	substrate = gdspy.fast_boolean(substrate,remove, 'not', 
		precision=1e-9, max_points=1000, layer=0)

poly_cell.add(substrate)


###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
