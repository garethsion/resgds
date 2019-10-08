#!/usr/bin/env python
import os
from resgds import *
from interface import Interface
import gdspy # gds library
import numpy as np
from restempfiles import *

# Layout filename
layout_file ='HalfWaveResonator.gds'

# Parameters
###################################################################
sub_x, sub_y = [5000, 5000] # substrate dimensions
coords = lambda x,dx=0: x+dx
x0,y0 = [1400,sub_y/2]

whw, ghw, lhw = [8.11, 17.85, 8108.45] # Cavity width, gap, length
whwtot = 2*ghw+whw

rfeed = 400
rhw = 100

rm_width = 4*whw + 2*ghw

sub_layer = 0
dot_layer = 1
cond_layer = 2
remove_layer = 3

conductor = []
removes = []

# Setup gds cell and gds object
poly_cell = gdspy.Cell('POLYGONS')
rs = Shapes(poly_cell)
rt = ResTempFiles(poly_cell)

# SUBSTRATE
#########################################################################
sub = [rs.rect(sub_x,sub_y,0,0)]

for i in range(0,len(sub)):
	sub = gdspy.Polygon(sub[i],sub_layer)
	poly_cell.add(sub)

# ANTI-DOTS
#########################################################################
layout = LayoutComponents(poly_cell, sub_x, sub_y,layer=dot_layer)
dots = layout.antidot_array(0,0,10,30,0)

# dot = rt.build(dots,poly_cell,input_layer=dot_layer)

# FEEDLINE
#########################################################################
feedwidth = 3000
feedl = 300
bondl = 600
bondh = feedl/2

input_length = 200
lcap = 35

lhw1 = 200

bondpad = rt.feedbond(x0,y0,whw,ghw,feedlength=feedl,bondlength=bondl,bondh=bondh,orientation='E')
# inbond = rt.build(bondpad,poly_cell,input_layer=cond_layer)

conductor = [rt.boolean(bondpad,conductor,input_layer=cond_layer,output_layer=cond_layer,mode='or')]

feed = rs.straight_trench(input_length, whw, ghw, x0, y0, orientation='H')

x1, y1 = [ coords(x0,input_length), coords(y0) ]
feed += [rs.rect(lcap,whwtot,x1,y1)]
# infeed = rt.build(feed,poly_cell,input_layer=cond_layer)
conductor += [rt.boolean(feed,conductor,input_layer=cond_layer,output_layer=cond_layer,mode='or')]


# FEEDLINE REMOVE
##########################################################################
bondr = rt.feedbond_remove(x0,y0,whw,ghw,feedlength=feedl,bondlength=bondl,bondh=bondh,orientation='E')
# bondrem = rt.build(bondr,poly_cell,input_layer=remove_layer)
removes += [rt.boolean(bondr,removes,input_layer=remove_layer,output_layer=remove_layer,mode='or')]

# INPUT FEEDLINE REMOVE
##########################################################################
feedr = [rs.rect(input_length+lcap,rm_width,x0,y0+whw/2+ghw-rm_width/2)]
# feedrem = rt.build(feedr,poly_cell,input_layer=remove_layer)
removes += [rt.boolean(feedr,removes,input_layer=remove_layer,output_layer=remove_layer,mode='or')]

# HALFWAVE RESONATOR
##########################################################################

qwlen,arc = rt.lengths(whw,ghw,rhw,lhw,lin=300,lout=300,no_arcs=4)

l_qw = .25 * np.pi * 242
l_hw = 2*l_qw

l1 = 300
lstrait = 1463
l2 = .5*lstrait - l_qw/2 - rhw/4 -whw/4

# print(2*l1 + 2*l_qw + 4*l_hw + 3*lstrait + 2*l2)

# resonator = rt.halfwaveresonator(x1,y1,whw,ghw,rhw,rhw,arc,lcap,qwlen[0],qwlen[1],qwlen[2])

x2, y2 = [ coords(x1,lcap), coords(y1) ]
resonator = rs.straight_trench(l1+lcap, whw, ghw, x1, y1, orientation='H')

x3, y3 = [ coords(x2,l1), coords(y1,rhw+whwtot) ]
resonator += rs.quarterarc_trench(rhw, whw, ghw, x3, y3, orient='SE')

x4, y4 = [ coords(x3,rhw), coords(y3) ]
resonator += rs.straight_trench(l2, whw, ghw, x4, y4, orientation='V')

x5, y5 = [ coords(x4,rhw+whwtot), coords(y4,l2) ]
resonator += rs.halfarc_trench(rhw, whw, ghw, x5, y5, orient='N')

x6, y6 = [ coords(x5,rhw), coords(y5) ]
resonator += rs.straight_trench(-lstrait, whw, ghw, x6, y6, orientation='V')

x7, y7 = [ coords(x6,rhw+whwtot), coords(y6,-lstrait) ]
resonator += rs.halfarc_trench(rhw, whw, ghw, x7, y7, orient='S')

x8, y8 = [ coords(x7,rhw), coords(y7) ]
resonator += rs.straight_trench(lstrait, whw, ghw, x8, y8, orientation='V')

x9, y9 = [ coords(x8,rhw+whwtot), coords(y8,lstrait) ]
resonator += rs.halfarc_trench(rhw, whw, ghw, x9, y9, orient='N')

x10, y10 = [ coords(x9,rhw), coords(y9) ]
resonator += rs.straight_trench(-lstrait, whw, ghw, x10, y10, orientation='V')

x11, y11 = [ coords(x10,rhw+whwtot), coords(y10,-lstrait) ]
resonator += rs.halfarc_trench(rhw, whw, ghw, x11, y11, orient='S')

x12, y12 = [ coords(x11,rhw), coords(y11) ]
resonator += rs.straight_trench(l2, whw, ghw, x12, y12, orientation='V')

x13, y13 = [ coords(x12,rhw+whwtot), coords(y12,l2) ]
resonator += rs.quarterarc_trench(rhw, whw, ghw, x13, y13, orient='NW')

x14, y14 = [ coords(x13), coords(y13,rhw) ]
resonator += rs.straight_trench(l1, whw, ghw, x14, y14, orientation='H')

# res = rt.build(resonator,poly_cell,input_layer=cond_layer)
conductor += [rt.boolean(resonator,conductor,input_layer=cond_layer,output_layer=cond_layer,mode='or')]

# RESONATOR REMOVES
###############################################################################

arcrad = .5*(2*rhw - ghw - whw)
arcrad += 0.78

x2r, y2r = [ coords(x2), coords(y1+ghw+whw/2 - rm_width/2) ]
resrem = [rs.rect(l1, rm_width, x2r, y2r)]

x3r, y3r = [ coords(x2r,l1), coords(y2r,arcrad+rm_width) ]
resrem += [rs.quarterarc(arcrad, rm_width, x3r, y3r, orientation='SE')]

x4r, y4r = [ coords(x3r,arcrad), coords(y3r) ]
resrem += [rs.rect(rm_width,l2, x4r, y4r)]

x5r, y5r = [ coords(x4r,arcrad+rm_width), coords(y4r,l2) ]
resrem += [rs.halfarc(arcrad, rm_width, x5r, y5r, orientation='N')]

x6r, y6r = [ coords(x5r,arcrad), coords(y5r) ]
resrem += [rs.rect(rm_width,-lstrait, x6r, y6r)]

x7r, y7r = [ coords(x6r,arcrad+rm_width), coords(y6r,-lstrait) ]
resrem += [rs.halfarc(arcrad,rm_width, x7r, y7r, orientation='S')]

x8r, y8r = [ coords(x7r,arcrad), coords(y7r) ]
resrem += [rs.rect(rm_width,lstrait, x8r, y8r)]

x9r, y9r = [ coords(x8r,arcrad+rm_width), coords(y8r,lstrait) ]
resrem += [rs.halfarc(arcrad,rm_width, x9r, y9r, orientation='N')]

x10r, y10r = [ coords(x9r,arcrad), coords(y9r) ]
resrem += [rs.rect(rm_width,-lstrait, x10r, y10r)]

x11r, y11r = [ coords(x10r,arcrad+rm_width), coords(y10r,-lstrait) ]
resrem += [rs.halfarc(arcrad,rm_width, x11r, y11r, orientation='S')]

x12r, y12r = [ coords(x11r,arcrad), coords(y11r) ]
resrem += [rs.rect(rm_width,l2, x12r, y12r)]

x13r, y13r = [ coords(x12r,arcrad+rm_width), coords(y12r,l2) ]
resrem += [rs.quarterarc(arcrad, rm_width, x13r, y13r, orientation='NW')]

x14r, y14r = [ coords(x13r), coords(y13r,arcrad) ]
resrem += [rs.rect(l1,rm_width, x14r, y14r)]

# resr = rt.build(resrem,poly_cell,input_layer=remove_layer)
removes += [rt.boolean(resrem,removes,input_layer=remove_layer,output_layer=remove_layer,mode='or')]

# OUTPUT FEEDBOND
############################################################################
x15, y15 = [ coords(x14,l1), coords(y14) ]
feed += [rs.rect(lcap,whwtot,x15,y15)]

x16, y16 = [ coords(x15), coords(y15) ]
feed += rs.straight_trench(input_length, whw, ghw, x16, y16, orientation='H')
# infeed = rt.build(feed,poly_cell,input_layer=cond_layer)
conductor += [rt.boolean(feed,conductor,input_layer=cond_layer,output_layer=cond_layer,mode='or')]

bondpad = rt.feedbond(x16+input_length,y16,whw,ghw,
	feedlength=feedl,bondlength=bondl,bondh=bondh,orientation='W')
# inbond = rt.build(bondpad,poly_cell,input_layer=cond_layer)
conductor += [rt.boolean(bondpad,conductor,input_layer=cond_layer,output_layer=cond_layer,mode='or')]

# OUTPUT BOND REMOVE
##########################################################################
bondr = rt.feedbond_remove(x16+input_length,y16,whw,ghw,feedlength=feedl,
	bondlength=bondl,bondh=bondh,orientation='W')

# bondrem = rt.build(bondr,poly_cell,input_layer=remove_layer)
removes += [rt.boolean(bondr,removes,input_layer=remove_layer,output_layer=remove_layer,mode='or')]

# OUTPUT FEEDLINE
##########################################################################
feed = rs.straight_trench(input_length, whw, ghw, x0, y0, orientation='H')

x1, y1 = [ coords(x0,input_length), coords(y0) ]
feed += [rs.rect(lcap,whwtot,x1,y1)]
# conductor += rt.boolean(feed,conductor,dots, input_layer=cond_layer, output_layer=dot_layer,mode='or')
# infeed = rt.build(feed,poly_cell,input_layer=cond_layer)
conductor += [rt.boolean(feed,conductor,input_layer=cond_layer,output_layer=cond_layer,mode='or')]

# OUTPUT FEEDLINE REMOVE
##########################################################################
feedr = [rs.rect(input_length+arcrad/2,rm_width,x16-arcrad/2,y16+ghw+whw/2-rm_width/2)]
# feedrem = rt.build(feedr,poly_cell,input_layer=remove_layer)
removes  += [rt.boolean(feedr,removes,input_layer=remove_layer,output_layer=remove_layer,mode='or')]

# MAKE GDS LAYERS
##########################################################################
# circuit = gdspy.fast_boolean(dots,conductor,'or',
# 	precision=1e-9, max_points=1000, layer=sub_layer)
# poly_cell.add(circuit)

dot = rt.build(dots,poly_cell,dot_layer)

poly_cell.add(conductor)
poly_cell.add(removes)

###########################################################################
# Make gds file and open up klayout
inter = Interface()
inter.klayout(layout_file)