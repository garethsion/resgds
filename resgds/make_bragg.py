#!/usr/bin/env python

import os
from resgds import *
import bragg 
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
glow = .5*(wc + 2*gc - wlow) #6.685 Gap of low impedance section
llow = 4051.32

whigh = 50 #2
ghigh = .5*(wlow + 2*glow - whigh)
lhigh = 4051.32

rlow = 50 # Radius of low impedance section
rhigh = 50

# Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# Substrate [layer 0]
sub = BuildRect(poly_cell, sub_x, sub_y, layer=0)
sub.make(0,0)

# Make Bragg Mirror sections
x0 = 0
y0 = sub_y/2

lowZ = bragg.Bragg(wlow, glow, llow, poly_cell, radius=rlow, layer=1)
highZ = bragg.Bragg(whigh, ghigh, lhigh, poly_cell, radius = rhigh, layer=1)

arr_l=np.repeat(np.arange(0,4),2*np.ones(4,dtype=int))
arr_h=np.append(arr_l[1:],[4], axis=0)

make_lowZ = lambda i: lowZ.mirror(x0 + arr_h[i]*highZ.mirror_width() + arr_l[i]*lowZ.mirror_width(), y0)
make_highZ = lambda i: highZ.mirror(x0 + arr_h[i]*highZ.mirror_width() + arr_l[i]*lowZ.mirror_width(), y0)
[make_lowZ(x) for x in range(len(arr_l)) if x % 2 == 0]
[make_highZ(x) for x in range(len(arr_l)) if x % 2 == 1]

# Check if klayout is already running. If not, write gds and open klayout.·
# If it is, just update the gds file
if("klayout" in (p.name() for p in psutil.process_iter())):
    #Write the pattern as a gds file
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
else:
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
    kl = call('./klayout_viewer %s' %layout_file,shell=True)
