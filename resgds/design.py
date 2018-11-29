#!/usr/bin/env python

import os
from resgds import *
import bragg
import gdspy # gds library
import numpy as np
from subprocess import call # Use to call kaloput_viewer bash script
import psutil # Use to check if klayout is running already   

def section_lengths(length,width,gap,radius):
    r1 = radius+gap
    r2 = r1 + width
    r3 = r2 + gap
    
    al1,al2,al3 = .5*[np.pi*r1, np.pi*r2, np.pi*r3]
    arclength = al3 - al2 -al1
    remain_length = length - 2*arclength

    l1,l2,l3 = [remain_length/6, remain_length/2, remain_length/3]
    print(l1+l2+l3 + 2*arclength)
    return l1, l2, l3

# Layout filename
layout_file = 'bragg.gds'

# Parameters
sub_x = 10000
sub_y = 10000
wc = 200 #8.11  Length of cavity
gc = 200 #17.85  Gap b/w conductor and substrate
lc = 8108.45 # Conductor width of cavity

wlow = 300  #30.44 Width of low impedance section
glow = 150 #6.685 Gap of low impedance section
llow = 4051.32

whigh = 50 #2
ghigh = 200 #20.905
lhigh = 4051.32

rext = 0 # extrude radius
rlow = 50 # Radius of low impedance section

# Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# Substrate [layer 0]
sub = BuildRect(poly_cell, sub_x, sub_y, layer=0)
sub.make(0,0)

coords = lambda x,dx=0: x+dx
#l1, l2, l3 = section_lengths(llow,wlow,glow,rext)

# Centre Cavity [layer 1]
x0, y0 = [coords(sub_x/2, -lc/2), coords(sub_y/2, -2*(wc/2) - gc/2)]

cavity = Trench(wc, gc, poly_cell, layer=1)
cavity.straight_trench(lc, x0, y0, orient='H')

# Low Impedance Sections [layer 1]
Zlow = Trench(wlow, glow, poly_cell, layer=1)
Zlow.halfarc_trench(rlow, x0, y0-rlow, orient='W', npoints=40)

# Low Z LHS extrusion straight trench
x1,y1 = [coords(x0), coords(y0,-2*rlow-2*glow-wlow)]
Zlow.quarterarc_trench(rext,x1,y1,orient='NE',npoints=20)

x2,y2 = [coords(x1),coords(y1,-2000)]
Zlow.straight_trench(2000, x2, y2, orient='V')

x3,y3 = [coords(x2, wlow + 2*glow + rlow),coords(y2)]
Zlow.halfarc_trench(rlow,x3,y3,orient='S',npoints=40)

x4,y4 = [coords(x3,rlow),coords(y3)]
Zlow.straight_trench(1000, x4, y4, orient='V')

# Check if klayout is already running. If not, write gds and open klayout. 
# If it is, just update the gds file
if("klayout" in (p.name() for p in psutil.process_iter())):
    #Write the pattern as a gds file
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
else:
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
    kl = call('./klayout_viewer %s' %layout_file,shell=True)

