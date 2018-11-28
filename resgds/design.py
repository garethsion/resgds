#!/usr/bin/env python

import os
from resgds import *
import gdspy # gds library
import numpy as np
from subprocess import call # Use to call kaloput_viewer bash script
import psutil # Use to check if klayout is running already   

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
rlow = 0 # Radius of low impedance section
nturns = 3 # Number of turns in quarter wavelength sections

# Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# Substrate [layer 0]
sub = BuildRect(poly_cell, sub_x, sub_y, layer=0)
sub.make(0,0)

# Centre Cavity [layer 1]
xc0 = sub_x/2 - lc/2 # x_position of cavity
yc0 = sub_y/2 - 2*(wc/2) - gc/2 # y_position of cavity
cavity = Trench(wc, gc, poly_cell, layer=1)
cavity.straight_trench(lc, xc0, yc0, orient='H')

# Low Impedance Sections [layer 1]
Zlow = Trench(wlow, glow, poly_cell, layer=1)
Zlow.quarterarc_trench(rlow, xc0, yc0, orient='NW', npoints=20)

# Low Z LHS extrusion straight trench
xl0 = xc0 - wlow-2*glow
yl0 = yc0 - 1000
Zlow.straight_trench(1000, xl0, yl0, orient='V')

# Low Z extrusion arc from straight section
xl1 = xl0 + wlow + 2*glow
yl1 = yl0
Zlow.quarterarc_trench(rlow, xl1, yl1, orient='SW', npoints=20)

# Low Z extrusion straight section from arc
xl2 = xl1
yl2 = yl1 -wlow - 2*glow
Zlow.straight_trench(1000, xl2, yl2, orient='H')

# Low Z extrusion arc fro straight section
xl3 = xl2 + 1000
yl3 = yl2
Zlow.quarterarc_trench(rlow, xl3, yl3, orient='NE', npoints=20)

# Low Z straight extrusion
xl4 = xl3
yl4 = yl3 - 2400
Zlow.straight_trench(2400, xl4, yl4, orient='V')

xl5 = xl3 + wlow + 2*glow
yl5 = yl4
Zlow.quarterarc_trench(rlow, xl5, yl5, orient='SW', npoints=20)

xl6 = xl5
yl6 = yl5 - wlow - 2*glow
Zlow.straight_trench(400, xl6, yl6, orient='H')

xl7 = xl6 + 400
yl7 = yl6 + wlow + 2*glow
Zlow.quarterarc_trench(rlow, xl7, yl7, orient='SE', npoints=20)

xl8 = xl7
yl8 = yl7 + 1000
Zlow.straight_trench(1000, xl7, yl7, orient='V')

# Check if klayout is already running. If not, write gds and open klayout. 
# If it is, just update the gds file
if("klayout" in (p.name() for p in psutil.process_iter())):
    #Write the pattern as a gds file
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
else:
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
    kl = call('./klayout_viewer %s' %layout_file,shell=True)

