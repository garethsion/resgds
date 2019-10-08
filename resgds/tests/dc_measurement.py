#!/usr/bin/env python
import os
from resgds.resonatorshapes import shapes as rs 
from resgds.resonatorshapes import restempfiles as rst
from resgds.braggshapes import bragg
from resgds.interface import interface
# from resgds import *
# import bragg
# from interface import Interface
import gdspy # gds library
import numpy as np
# from restempfiles import *

# Layout filename
layout_file ='dc_measurement.gds'

# CPW Parameters
###########################################################################
sub_x, sub_y = [9000, 4000] # substrate dimensions

def DC_contacts_etch(x0, y0, w, l, bond, gap, contacts=4):
    x0 = float(x0)
    y0 = float(y0)
    shapes = []
    shapes += [rs.rect(4*bond + l + 4*gap, gap, 0, 0)]
    shapes += [rs.rect(gap, bond, 0, gap)]
    shapes += [rs.rect(bond*2 + gap*3, gap, 0, gap + bond)]
    shapes += [rs.rect(gap, bond - w, bond + gap, gap + w)]
    shapes += [rs.rect(bond - gap, gap, bond + 2* gap, gap + w)]
    shapes += [rs.rect(gap, bond, 2*bond + 2*gap, gap + w)]
    shapes += [rs.rect(l - 2*gap, gap, 2*bond + 3*gap, gap + w)]
    shapes += [rs.rect(gap, bond, 2*bond + gap + l, gap + w)]
    shapes += [rs.rect(2*bond + 2*gap, gap, 2*bond + 2*gap + l, gap + bond)]
    shapes += [rs.rect(gap, bond , 3*bond + 2*gap + l, gap + w)]
    shapes += [rs.rect(gap, bond + w , 4*bond + 3*gap + l, gap)]
    shapes += [rs.rect(bond - gap, gap, 2*bond + 3*gap+ l, gap + w)]
   
    # shapes = [move(i, x0, y0) for i in shapes]
   
    return shapes
    
w = 2
gap = 10
l = 300
bond = 200

dc = DC_contacts_etch(0,0,w,l,bond,gap)

for i in range(0,len(dc)):
	dcm = gdspy.Polygon(dc[i],0)
	poly_cell.add(dcm)

###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)