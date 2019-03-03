import os
import res_shapes as rs
import gdspy
from interface import Interface
import numpy as np

# Layout filename
layout_file ='oscar.gds'

poly_cell = gdspy.Cell('POLYGONS')

gaps = [10, 25, 50, 75, 100]
ccs = [45, 50, 55]
r = 500
lcap = 100
lstart = 100
c_gap = 1
#resonator - 3 element list [coarse res elements, fine res elements, stuff to remove from ground plane]


#res
poly_cell.elements=[]
cc = ccs[0]
gap = gaps[4]
res = rs.hw_sim(cc, gap, r, lcap, lstart, c_gap)

print(res[0])

for i in res[0]:
    poly_cell.add(gdspy.Polygon(i, 2))
        
grnd = rs.rect(res[2], res[3] + 1000, 0, - (res[3] + 1000)/2)
grnd_poly = gdspy.Polygon(grnd, 0)
    
ps = []
for i in res[1]:
    ps.append(gdspy.Polygon(i, 1))
for i in ps:
    grnd_poly = gdspy.fast_boolean(grnd_poly, i, 'not', precision=1e-9, max_points=1000, layer=0)
    
        
        
#add all polygons to cells
#poly_cell.add(grnd_poly)



# for j in range(len(gaps)*len(ccs)):
#     #res
#     poly_cell.elements=[]
#     cc = ccs[int(j/len(gaps))]
#     gap = gaps[j%len(gaps)]
#     res = rs.hw_sim(cc, gap, r, lcap, lstart, c_gap)
    
#     for i in res[0]:
#         poly_cell.add(gdspy.Polygon(i, 2))
        
#     grnd = rs.rect(res[2], res[3] + 1000, 0, - (res[3] + 1000)/2)
#     grnd_poly = gdspy.Polygon(grnd, 0)
    
#     ps = []
#     for i in res[1]:
#         ps.append(gdspy.Polygon(i, 1))
#     for i in ps:
#         print(i)
#         grnd_poly = gdspy.fast_boolean(grnd_poly, i, 'not', precision=1e-9, max_points=1000, layer=0)
    
        
        
#     #add all polygons to cells
#     poly_cell.add(grnd_poly)
    
    # poly_cell.add(res_coarse_poly)
    # poly_cell.add(res_fine_poly)
    
    #Write the pattern as a gds file

###########################################################################
# Make gds file and open up klayout
# inter = Interface()
# inter.klayout(layout_file)