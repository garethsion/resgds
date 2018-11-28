#!/usr/bin/env python

class CPWGDS:

    def __init__(self):
        return

    def waveguide(self,path,points,finish,bend_radius,
            number_of_points=0.01,direction=None,
            layer=0,datatype=0):
        """
        Creates a waveguide - adapted from Lucas Heitzmann Gabrielli example
        
        path             : starting 'gdspy.Path'
        points           : coordinates along which waveguide will travel
        finish           : end point of the waveguide
        bend_radius      : radius of the turns in the waveguide
        number_of_points : same as in 'path.turn'
        direction        : starting direction
        layer            : GDSII layer number
        datatype         : GDSII datatype number

        Return 'path'
        """
    if direction is not None:
        path.direction = direction
    axis = 0 if path.direction[1] == 'x' else 1
    points.append(finish[(axis + len(points)) % 2])
    n = len(points)
    
    if points[0] > (path.x, path.y)[axis]:
        path.direction = ['+x', '+y'][axis]
    else:
        path.direction = ['-x', '-y'][axis]
    
    for i in range(n):
        path.segment(
            abs(points[i] - (path.x, path.y)[axis]) - bend_radius,
            layer=layer,
            datatype=datatype)
        axis = 1 - axis
        if i < n - 1:
            goto = points[i + 1]
        else:
            goto = finish[axis]
        if (goto > (path.x, path.y)[axis]) ^ ((path.direction[0] == '+') ^
                                              (path.direction[1] == 'x')):
            bend = 'l'
        else:
            bend = 'r'
        path.turn(
            bend_radius,
            bend,
            number_of_points=number_of_points,
            layer=layer,
            datatype=datatype)
    
        return path.segment(
        abs(finish[axis] - (path.x, path.y)[axis]),
        layer=layer,
        datatype=datatype)

    def substrate(self):
        return
