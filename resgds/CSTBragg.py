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
lcav1, lcav2, lcav3 = [1000, 5500, 1000]
taper_length = 100

cav_x0,cav_y0 = [coords(xb_strt),coords(yb_strt,-lcav1)]
cav_cond = [rs.rect(wc,lcav1-taper_length, cav_x0, cav_y0)]

cav_xtaper, cav_ytaper = [coords(xb_strt),coords(yb_strt,-taper_length)]
print(cav_xtaper)
print(cav_ytaper)

taper = [rs.exptaper(wc, wlow, taper_length, cav_xtaper)]

# print('cav = ',cav_cond[0][0]),'\n'
# print('taper = ',taper)
print(cav_cond)

# print(np.shape(list(taper)))

tap = gdspy.Polygon(taper[0],2)
poly_cell.add(tap)

# for i in range(0,len(taper)):
# 	tap = gdspy.Polygon(taper[i],2)
# 	poly_cell.add(tap)

# for i in range(0,len(cav_cond)):
# 	cavity = gdspy.Polygon(cav_cond[i],1)
# 	poly_cell.add(cavity)

# cav_xtaper, cav_ytaper = [coords(xb_strt),coords(yb_strt,-taper_length)]

# # cavity.thinning_trench(w1, w2, rat, cav_xtaper, cav_ytaper, 
# #         taper_length, orientation='N',strait=strait)

# cavity.taper(wc, gc, wlow, glow, cav_x0, 
#         cav_y0+lcav1-taper_length, cav_x0, cav_y0+lcav1)

# cav_x1,cav_y1 = [coords(xb_strt,-rlow),coords(yb_strt,-lcav1)]
# cavity.halfarc_trench(rlow,cav_x1,cav_y1,orient='S',npoints=40)

# cav_x2,cav_y2 = [coords(xb_strt,-2*rlow-wlow-2*glow),coords(yb_strt,-lcav1)]
# cavity.straight_trench(lcav2,cav_x2,cav_y2,orient='V')

# cav_x3,cav_y3 = [coords(xb_strt,-rlow),coords(yb_strt,lcav2-lcav1)]
# cavity.halfarc_trench(rlow,cav_x3,cav_y3,orient='N',npoints=40)

# cav_x4,cav_y4 = [coords(xb_strt),coords(yb_strt,lcav2-lcav1-lcav3+taper_length)]
# cavend = cavity.straight_trench(lcav3-taper_length,cav_x4,cav_y4,orient='V')

# cavity.taper(wlow, glow, wc, gc, cav_x4, 
#        cav_y4-taper_length, cav_x4, cav_y4)














# # Cavity [layer 0]
# # I assign coordinates first, and then build geometries accordingly
# ############################################################################
# coords = lambda x,dx=0: x+dx
# xb_strt,yb_strt = [coords(725),coords(sub_y/2)- lext2 - lext3 - 140]
# lcav1, lcav2, lcav3 = [1000, 5500, 1000]
# taper_length = 100

# w_cr = wc + 2*gc

# cav_x0,cav_y0 = [coords(xb_strt),coords(yb_strt,-lcav1)]

# cav = [rs.rect(w_cr, lcav2,cav_x0, cav_y0)]
# cav += [rs.halfarc(rlow,w_cr,cav_x0+rlow+w_cr,cav_y0,orientation='S')] 
# cav += [rs.rect(w_cr, lcav1,cav_x0+rlow+w_cr+rlow, cav_y0)]

# for i in range(0,len(cav)):
# 	#poly_cell.add(gdspy.Polygon(cav[i],1))
# 	cavity = gdspy.Polygon(cav[i],1)
# 	substrate = gdspy.fast_boolean(substrate,cavity, 'not', 
# 		precision=1e-9, max_points=1000, layer=0)

# poly_cell.add(substrate)

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
