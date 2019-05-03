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
layout_file ='cst_test1.dxf'

# Parameters
#__________________________________________________________
sub_x, sub_y = [1000, 500] # substrate dimensions
wc, gc, lc = [8.11, 17.85, 8108.45] # Cavity width, gap, length
wlow, llow = [30.44, 4051.32]  # Low Z section
whigh, lhigh = [2, 4051.32] # High Z section
glow, ghigh = [.5*(wc + 2*gc - wlow),.5*(wc + 2*gc - whigh)]

# Start making resonator geometry
############################################################################

# # Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# Substrate coordinate list
sub_layer = 0
sub = rs.rect(sub_x,sub_y,0,0)
substrate = gdspy.Polygon(sub, layer=0)

coords = lambda x,dx=0: x+dx

Lstub = 50
gstub = 5

Lcav=sub_x - 2*Lstub-2*gstub

x0 = 0
y0 = sub_y/2 - wlow/2

# Conductor (layer 1)
cond_layer = 1

cond = [rs.rect(Lstub,wlow,x0,y0)]

x1,y1 = [coords(x0,Lstub+gstub),coords(y0)]
cond += [rs.rect(Lcav,wlow,x1,y1)] 

x2,y2 = [coords(x1,Lcav+gstub),coords(y0)]
cond += [rs.rect(Lstub,wlow,x2,y2)] 

for i in range(0,len(cond)):
	conductor = gdspy.Polygon(cond[i],cond_layer)
	poly_cell.add(conductor)

# Remove from grnd
rem_width = 2*(glow+wlow)
cond_rem = [rs.rect(sub_x,wlow+2*glow,x0,sub_y/2-rem_width/2+wlow/2)]

# conductor = gdspy.Polygon(cond_rem[0],2)
# poly_cell.add(conductor)

for i in range(0,len(cond_rem)):
	#poly_cell.add(gdspy.Polygon(cav[i],1))
	remove = gdspy.Polygon(cond_rem[i],cond_layer)
	substrate = gdspy.fast_boolean(substrate,remove, 'not', 
		precision=1e-9, max_points=1000, layer=sub_layer)

poly_cell.add(substrate)

# cav_cond = [rs.rect(wc, lcav2,cav_x0+gc, cav_y0)]
# cav_cond += [rs.halfarc(rlow+gc,wc,cav_x0+rlow+wc+2*gc,cav_y0,orientation='S')] 
# cav_cond += [rs.rect(wc, lcav1,cav_x0+rlow+wc+3*gc+rlow, cav_y0)]

# for i in range(0,len(cav_cond)):
# 	#poly_cell.add(gdspy.Polygon(cav[i],1))
# 	cavity = gdspy.Polygon(cav_cond[i],1)
# 	poly_cell.add(cavity)


###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)
