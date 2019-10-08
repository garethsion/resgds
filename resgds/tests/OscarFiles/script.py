import os
os.chdir(r'C:\Users\ok_78\Dropbox\UCLQ Fellowship\Devices\EBL\scripting')
import res_shapes as rs
import gdspy


#setup the folder and gds 'cell'
poly_cell = gdspy.Cell('POLYGONS')
folder = r'C:\Users\ok_78\Dropbox\UCLQ Fellowship\2019\CDT lab\CDT_lab'

#layer 0 - rectangle showing chip size. Not to be exposed.
chip_w = 8000
chip_h = 8000
d_dots = 10
dot_size=10
poly = gdspy.Polygon(rs.rect(chip_w, chip_h, 0, 0), 0)
poly_cell.add(poly)

# # layer 1 - Antidot array covering chip


#layer 2 - Feed line 10, .5, 300, 250, 1500, 3000, 2
bond_pad = 400
central_conductor = 35
ratio = 0.5
H = 1000
W = 3000
r = 500
feedline_x = 1500
feedline_y = 1500 

feedline = rs.feedline(central_conductor, ratio, r, W, H, bond_pad, d_dots)
feedline_remove = feedline[1]
feedline_remove = [rs.move(i, feedline_x, feedline_y) for i in feedline_remove]
feedline = feedline[0]


feedline = [rs.move(i, feedline_x, feedline_y) for i in feedline]
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


res1 = rs.quarterwave(res_cc, res_cc*ratio, 5, 100, 510, 100, ltail=100, flip_y='True', constriction=False, SQUID=False)
res1_x = 2500
res1_coarse = [rs.move(i, res1_x, feedline_top + feedline_sep + feedline_y) for i in res1[0]]
res1_fine = [rs.move(i, res1_x, feedline_top + feedline_sep + feedline_y) for i in res1[1]]
res1_remove = [rs.move(i, res1_x, feedline_top + feedline_sep + feedline_y) for i in res1[2]]
for i in res1_coarse:
    poly_cell.add(gdspy.Polygon(i, 4))
for i in res1_fine:
    poly_cell.add(gdspy.Polygon(i, 4))
    
    
res2 = rs.quarterwave(res_cc, res_cc*ratio, 5, 100, 480, 100, ltail=100, flip_y='True', constriction=False, SQUID=False)
res2_x = 5000
res2_coarse = [rs.move(i, res2_x, feedline_top + feedline_sep + feedline_y) for i in res2[0]]
res2_fine = [rs.move(i, res2_x, feedline_top + feedline_sep + feedline_y) for i in res2[1]]
res2_remove = [rs.move(i, res2_x, feedline_top + feedline_sep + feedline_y) for i in res2[2]]
for i in res2_coarse:
    poly_cell.add(gdspy.Polygon(i, 4))
for i in res2_fine:
    poly_cell.add(gdspy.Polygon(i, 4))
    
res3 = rs.quarterwave(res_cc, res_cc*ratio, 5, 100, 450, 100, ltail=100,constriction=False, SQUID=False)
res3_x = 3200
res3_coarse = [rs.move(i, res3_x, feedline_bot - feedline_sep + feedline_y) for i in res3[0]]
res3_fine = [rs.move(i, res3_x, feedline_bot - feedline_sep + feedline_y) for i in res3[1]]
res3_remove = [rs.move(i, res3_x, feedline_bot - feedline_sep + feedline_y) for i in res3[2]]
for i in res3_coarse:
    poly_cell.add(gdspy.Polygon(i, 4))
for i in res3_fine:
    poly_cell.add(gdspy.Polygon(i, 4))
    
res4 = rs.quarterwave(res_cc, res_cc*ratio, 5, 100, 420, 100, ltail=100, d_dots=d_dots, constriction=False, SQUID=False)
res4_x = 4500
res4_coarse = [rs.move(i, res4_x, feedline_bot - feedline_sep + feedline_y) for i in res4[0]]
res4_fine = [rs.move(i, res4_x, feedline_bot - feedline_sep + feedline_y) for i in res4[1]]
res4_remove = [rs.move(i, res4_x, feedline_bot - feedline_sep + feedline_y) for i in res4[2]]
for i in res4_coarse:
    poly_cell.add(gdspy.Polygon(i, 4))
for i in res4_fine:
    poly_cell.add(gdspy.Polygon(i, 4))
    
DC = rs.DC_contacts_etch(4800, 5800, 10, 100, 300, 10)
for i in DC:
    poly_cell.add(gdspy.Polygon(i, 5))

#Write the pattern as a gds file
os.chdir(folder)
gdspy.write_gds('chip_test.gds', unit=1.0e-6, precision=1.0e-9)
# gdspy.LayoutViewer()