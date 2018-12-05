#!/usr/bin/env python

import os
from resgds import *
import bragg
import gdspy # gds library
import numpy as np
from subprocess import call # Use to call kaloput_viewer bash script
import psutil # Use to check if klayout is running already   

# Layout filename
layout_file = 'bond.gds'

# Parameters
sub_x = 10000
sub_y = 10000

wc = 8.11 # Conductor width of cavity
gc = 17.85 # Gap b/w conductor and substrate
lc = 8108.45 # Length of cavity

# Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)

# Make feedline sections
cc = 4*gc
ratio = .5

bond_pad = 200
rfeed = 100

# Feedline
feedin_length = 691.045
feedlink_length = 885
feedline = Trench(gc,wc+2*gc,poly_cell, layer=2)

# Feedbond
feed = LayoutComponents(poly_cell, 0, 0, layer=2)
feedbond = feed.make_feedbond(cc, ratio, bond_pad, sub_x+bond_pad/2, bond_pad, orientation='H')
#feedline.straight_trench(feedlink_length, sub_x-feedlink_length, bond_pad, orient='H')
feedline.straight_trench(feedlink_length, feedbond[2][2][0]-feedlink_length, feedbond[2][2][1], orient='H')

# Check if klayout is already running. If not, write gds and open klayout. 
# If it is, just update the gds file
if("klayout" in (p.name() for p in psutil.process_iter())):
    #Write the pattern as a gds file
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
else:
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
    kl = call('./klayout_viewer %s' %layout_file,shell=True)

