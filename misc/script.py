#!/usr/bin/env python

import os
import psutil
import res_shapes as rs
import gdspy
import numpy as np
from subprocess import call

#setup the folder and gds 'cell'
poly_cell = gdspy.Cell('POLYGONS')
layout_file = 'oscar.gds'

#layer 0 - rectangle showing chip size. Not to be exposed.
chip_w = 7500
chip_h = 7500
d_dots = 20
poly = gdspy.Polygon(rs.rect(chip_w, chip_h, 0, 0), 0)
poly_cell.add(poly)

# layer 1 - Antidot array covering chip
dots = rs.antidot_array(0, 0, 7500, 7500, 10, 20, 0)
for i in dots:
    poly_cell.add(gdspy.Polygon(i, 1))

#layer 2 - Feed line 10, .5, 300, 250, 1500, 3000, 2
bond_pad = 200
central_conductor = 50
ratio = 0.5
H = 1000
W = 4000
r = 500

feedline = rs.feedline(central_conductor, ratio, r, W, H, bond_pad, d_dots)
feedline_remove = feedline[1]
feedline_remove = [rs.move(i, 1000, 1000) for i in feedline_remove]
feedline = feedline[0]


feedline = [rs.move(i, 1000, 1000) for i in feedline]
for i in feedline:
    poly_cell.add(gdspy.Polygon(i, 2))

#layer 3 & 4- Resonators coarse & fine

# def quarterwave(w, gap, nturns, lcap, lmeander, r, tail=True, ltail=100, 
#                 constriction=True, constrictionw=1, constrictionr=.5, spacer=5,
#                 SQUID=True, squid_loop=2, squid_constriction=0.5, 
#                 flip_y='False'):
feedline_sep = 30
feedline_top = bond_pad*(2 + ratio) + H + r + central_conductor*(1 + 2*ratio)
feedline_bot = bond_pad*(2 + ratio) + H + r
res_cc = 10


res1 = rs.quarterwave(res_cc, res_cc*ratio, 5, 100, 500, 100, flip_y='True', d_dots=d_dots, constriction=False, SQUID=True)
res1_x = 2500
res1_coarse = [rs.move(i, res1_x, feedline_top + 30 + 1000) for i in res1[0]]
res1_fine = [rs.move(i, res1_x, feedline_top + 30 + 1000) for i in res1[1]]
res1_remove = [rs.move(i, res1_x, feedline_top + 30 + 1000) for i in res1[2]]
for i in res1_coarse:
    poly_cell.add(gdspy.Polygon(i, 3))
for i in res1_fine:
    poly_cell.add(gdspy.Polygon(i, 4))
    
    
res2 = rs.quarterwave(res_cc, res_cc*ratio, 5, 100, 400, 100, ltail=200, flip_y='True', d_dots=d_dots, constriction=False)
res2_x = 5500
res2_coarse = [rs.move(i, res2_x, feedline_top + 30 + 1000) for i in res2[0]]
res2_fine = [rs.move(i, res2_x, feedline_top + 30 + 1000) for i in res2[1]]
res2_remove = [rs.move(i, res2_x, feedline_top + 30 + 1000) for i in res2[2]]
for i in res2_coarse:
    poly_cell.add(gdspy.Polygon(i, 3))
for i in res2_fine:
    poly_cell.add(gdspy.Polygon(i, 4))
    
res3 = rs.quarterwave(res_cc, res_cc*ratio, 5, 100, 450, 100, ltail=300, d_dots=d_dots, constriction=False)
res3_x = 3200
res3_coarse = [rs.move(i, res3_x, feedline_bot - 30 + 1000) for i in res3[0]]
res3_fine = [rs.move(i, res3_x, feedline_bot - 30 + 1000) for i in res3[1]]
res3_remove = [rs.move(i, res3_x, feedline_bot - 30 + 1000) for i in res3[2]]
for i in res3_coarse:
    poly_cell.add(gdspy.Polygon(i, 3))
for i in res3_fine:
    poly_cell.add(gdspy.Polygon(i, 4))
    
res4 = rs.quarterwave(res_cc, res_cc*ratio, 5, 100, 550, 100, ltail=800, d_dots=d_dots, constriction=False, SQUID=False)
res4_x = 4700
res4_coarse = [rs.move(i, res4_x, feedline_bot - 30 + 1000) for i in res4[0]]
res4_fine = [rs.move(i, res4_x, feedline_bot - 30 + 1000) for i in res4[1]]
res4_remove = [rs.move(i, res4_x, feedline_bot - 30 + 1000) for i in res4[2]]
for i in res4_coarse:
    poly_cell.add(gdspy.Polygon(i, 3))
for i in res4_fine:
    poly_cell.add(gdspy.Polygon(i, 4))
    
#layer 5 - Flux lines coarse
bond_pad = 200
central_conductor = 40
ratio = 0.1
H = 1000
W = 200
r = 200

fluxline1 = rs.feedline(central_conductor, ratio, r, W, H, bond_pad, d_dots)
fluxline1_remove = fluxline1[1]
fluxline1_remove = [rs.flip(i) for i in fluxline1_remove]
fluxline1 = fluxline1[0]
fluxline1 = [rs.flip(i) for i in fluxline1]


fluxline_sep = 20
fluxline_top = bond_pad*(2 + ratio) + H + r + central_conductor*(1 + 2*ratio)
fluxline_right = (0.5 + ratio)*(3*central_conductor + bond_pad) + W + 2*r

dx = res1_fine[-2][-1][0] - fluxline_right - fluxline_sep
dy = fluxline_top + res1_fine[-2][-1][1] - r - central_conductor*(1 + 2*ratio)

fluxline1 = [rs.move(i, dx, dy) for i in fluxline1]
fluxline1_remove = [rs.move(i, dx, dy) for i in fluxline1_remove]

for i in fluxline1:
    poly_cell.add(gdspy.Polygon(i, 5))

fluxline2 = rs.feedline(central_conductor, ratio, r, W, H, bond_pad, d_dots)
fluxline2_remove = fluxline2[1]
fluxline2_remove = [rs.flip(i) for i in fluxline2_remove]
fluxline2 = fluxline2[0]
fluxline2 = [rs.flip(i) for i in fluxline2]


fluxline_sep = 10
fluxline_top = bond_pad*(2 + ratio) + H + r + central_conductor*(1 + 2*ratio)
fluxline_right = (0.5 + ratio)*(3*central_conductor + bond_pad) + W + 2*r

dx = res2_fine[-2][-1][0] - fluxline_right - fluxline_sep
dy = fluxline_top + res2_fine[-2][-1][1] - r - central_conductor*(1 + 2*ratio)

fluxline2 = [rs.move(i, dx, dy) for i in fluxline2]
fluxline2_remove = [rs.move(i, dx, dy) for i in fluxline2_remove]

for i in fluxline2:
    poly_cell.add(gdspy.Polygon(i, 5))

# feedline = rs.feedline(central_conductor, ratio, r, W, H, bond_pad, d_dots)
# feedline_remove = feedline[1]
# feedline_remove = [rs.move(i, 1000, 1000) for i in feedline_remove]
# feedline = feedline[0]
# 
# 
# feedline = [rs.move(i, 1000, 1000) for i in feedline]
# for i in feedline:
#     poly_cell.add(gdspy.Polygon(i, 2))

# fluxline = rs.feedline(central_conductor, ratio, r, W, H, bond_pad, d_dots)
# fluxline = [rs.flip(i) for i in fluxline]


#layer 6 - Flux lines fine

#layer 7 - 

#layer 8 - outlines of shapes to remove antidots within
for i in feedline_remove:
    poly_cell.add(gdspy.Polygon(i, 8))
for i in res1_remove:
    poly_cell.add(gdspy.Polygon(i, 8))
for i in res2_remove:
    poly_cell.add(gdspy.Polygon(i, 8))
for i in res3_remove:
    poly_cell.add(gdspy.Polygon(i, 8))
for i in res4_remove:
    poly_cell.add(gdspy.Polygon(i, 8))
for i in fluxline1_remove:
    poly_cell.add(gdspy.Polygon(i, 8))
for i in fluxline2_remove:
    poly_cell.add(gdspy.Polygon(i, 8))


if("klayout" in (p.name() for p in psutil.process_iter())):
    #Write the pattern as a gds file
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
else:
    gdspy.write_gds(layout_file, unit=1.0e-6, precision=1.0e-9)
    kl = call('./klayout_viewer %s' %layout_file,shell=True)
