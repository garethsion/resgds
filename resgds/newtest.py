#!/usr/bin/env python

import os
from resgds import *
import gdspy # gds library
import numpy as np
from subprocess import call # Use to call kaloput_viewer bash script
import psutil # Use to check if klayout is running already···

# Layout filename
layout_file = 'test.gds'

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
rlow = 100 # Radius of low impedance section
nturns = 3 # Number of turns in quarter wavelength sections

# Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# Substrate [layer 0]
sub = BuildRect(poly_cell, sub_x, sub_y, layer=0)
sub.make(0,0)

# Bragg
x0 = sub_x/2
y0 = sub_y/2
l1 = 1000
mirror = Trench(wlow, glow, poly_cell, layer=1)
mirror.straight_trench(l1,x0,y0,orient='V')

x1 = x0 +wlow + 2*glow + rlow
y1 = y0 + l1
mirror.halfarc_trench(rlow, x1, y1, orient='N', npoints=40)

l2 = 3000
x2 = x1 + rlow
y2 = y1 - l2 
mirror.straight_trench(l2,x2,y2,orient='V')

x3 = x2 + wlow + 2*glow + rlow
y3 = y2
mirror.halfarc_trench(rlow, x3, y3, orient='S', npoints=40)

l3 = l2-l1
x4 = x3 + rlow
y4 = y3
mirror.straight_trench(l3,x4,y4,orient='V')

# Check if klayout is already running. If not, write gds and open klayout.·
# If it is, just update the gds file
if("klayout" in (p.name() for p in psutil.process_iter())):
    #Write the pattern as a gds file
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
else:
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
    kl = call('./klayout_viewer %s' %layout_file,shell=True)
