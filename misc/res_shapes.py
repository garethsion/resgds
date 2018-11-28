#!/usr/bin/env python

import numpy as np

def move(shape, dx, dy):
    return [(i[0] + dx, i[1] + dy) for i in shape]

def flip(shape, axis='y'):
    if axis =='y':
        return [(i[0], -i[1]) for i in shape]
    elif axis =='x':
        return [(-i[0], i[1]) for i in shape]

def circ_arc(r, x0, y0, n=50, theta0=0, thetaf=np.pi/2):
    '''
    List of tuples giving x, y coords of a circular arc from theta_0 to theta_f
    with centre at (x0, y0) and radius r.
    '''
    return [(r*np.cos(i) + x0, r*np.sin(i) + y0)
                        for i in np.linspace(theta0, thetaf, n)]

def halfarc(r, w, x0, y0, orientation='E', npoints=40):
    '''
    List of tuples.
    A half circle trench of width w, the inner side of which is a circle with
    radius r and centre (x0, y0). Different orientations of points of compass
    with 'N' meaning that the semicircle is an arc that looks like a rainbow.
    '''
    if orientation == 'N':
        t0=0
        tf=np.pi
    elif orientation == 'E':
        t0=-np.pi/2
        tf=np.pi/2
    elif orientation == 'W':
        t0=np.pi/2
        tf=3*np.pi/2
    elif orientation == 'S':
        t0=np.pi
        tf=2*np.pi

    inner = circ_arc(r, x0, y0, n=npoints, theta0=t0, thetaf=tf)
    outer = circ_arc(r + w, x0, y0, n=npoints, theta0=t0, thetaf=tf)[::-1]

    return inner + outer

def halfarc_trench(r, width, gap, x0, y0, orient='E', npoints=40):
    inside = halfarc(r, gap, x0, y0, orientation=orient, npoints=npoints)
    outside = halfarc(r + gap + width, gap, x0, y0, orientation=orient, npoints=npoints)
    return [inside, outside]

def quarterarc(r, w, x0, y0, orientation='NE', npoints=20):
    if orientation == 'NE':
        t0=0
        tf=np.pi/2
    elif orientation == 'SE':
        t0=3*np.pi/2
        tf=2*np.pi
    elif orientation == 'SW':
        t0=np.pi
        tf=3*np.pi/2
    elif orientation == 'NW':
        t0=np.pi/2
        tf=np.pi

    inner = circ_arc(r, x0, y0, theta0=t0, thetaf=tf, n=npoints)
    outer = circ_arc(r + w, x0, y0, theta0=t0, thetaf=tf, n=npoints)[::-1]

    return inner + outer

def quarterarc_trench(r, width, gap, x0, y0, orient='NE', npoints=20):
    inside = quarterarc(r, gap, x0, y0, orientation=orient, npoints=npoints)
    outside = quarterarc(r + gap + width, gap, x0, y0, orientation=orient, npoints=npoints)
    return [inside, outside]

def rect(w, l, x0, y0):
    '''
    List of tuples
    Recangle of width and length w and l with bottom left corner at (x0, y0).
    '''
    return [(x0, y0), (x0 + w, y0), (x0 + w, y0 + l), (x0, y0 + l)]

def straight_trench(l, gap, w, x0, y0, orientation='H'):
    if orientation == 'H':
        return [rect(l, gap, x0, y0), rect(l, gap, x0, y0 + gap + w)]
    if orientation == 'V':
        return [rect(gap, l, x0, y0), rect(gap, l, x0 + gap + w, y0)]

def thinning_trench(w1, w2, gap, x0, y0, orientation='V'):
    '''
    list of list of tuples
    '''
    w1 = float(w1)
    w2 = float(w2)
    if w1 > w2:
        d1 = [(x0, y0), (x0, y0 +  w1), (x0 + gap, y0 + w1), (x0 + gap + (w1 - w2)/2, y0)]
        d2 = [(x0 + w1 + 2*gap, y0), (x0 + w1 + 2*gap, y0 +  w1), (x0 + w1 + gap, y0 + w1), (x0 + gap + (w1 - w2)/2 + w2, y0)]
    else:
        d1 = [(x0, y0 - w2), (x0, y0 ), (x0 + gap + (w2 - w1)/2, y0 ), (x0 + gap , y0 - w2)]
        d2 = [(x0 + w2 + 2*gap, y0 - w2), (x0 + w2 + gap, y0 - w2), (x0 + gap + (w2 - w1)/2 + w1, y0), (x0 + w2 +2*gap, y0)]
    return [d1, d2]

def thinning_trench_style_2(w1, w2, rat, x0, y0, H):
    '''
    list of list of tuples
    '''
    w1 = float(w1)
    w2 = float(w2)
    d1 = [(x0, y0), (x0 + w1*rat, y0), (x0 + w1*(rat + .5) - w2*.5, y0 + H), (x0 + w1*(rat + .5) - w2*(rat + .5), y0 + H)]
    d2 = [(x0 + w1*(1 + rat), y0), (x0 + w1*(1 + 2*rat), y0), (x0 + w1*(rat + .5) + w2*(rat + .5), y0 + H), (x0 + w1*(rat + .5) + w2*.5, y0 + H)]
    return [d1, d2]

def quarterwave(w, gap, nturns, lcap, lmeander, r, tail=True, ltail=100,
                constriction=True, constrictionw=1, constrictionr=.5, spacer=5,
                SQUID=True, SQUID_H=2, SQUID_r = .8, SQUID_constriction=0.5,
                flip_y='False', d_dots=5, SQUID_con_H=.2):
    '''
    List of list of list of tuples.
    There are two lists denoting different parts of the resonator. One list is
    the capacitor, meanders and part of the tail. Second list contains the fine
    shapes. This allows these to be saved to different laye
    '''
    cap = straight_trench(lcap, gap, w, gap, 0) + [rect(gap, 2*gap + w, 0, 0)]
    remove = [rect(gap + d_dots, 2*gap + w + 2*d_dots, - d_dots, -d_dots)]
    remove += [rect(lcap, 2*(gap + d_dots) + w, gap, -d_dots)]
    arccentre = [gap + lcap, -r]
    meanders = []
    for turn in range(nturns):
        if turn%2 == 0:
            o = 'E'
            meanders += halfarc_trench(r, w, gap, arccentre[0], arccentre[1], orient=o)
            remove += [halfarc(r - d_dots, w + 2*gap + 2*d_dots, arccentre[0], arccentre[1], orientation=o)]
            meanders += straight_trench(lmeander, gap, w, arccentre[0] - lmeander, arccentre[1] - r - 2*gap - w)
            remove += [rect(lmeander, 2*gap + w + 2*d_dots, arccentre[0] - lmeander, arccentre[1] - r - 2*gap - w - d_dots)]
            arccentre = [arccentre[0] - lmeander, arccentre[1] - 2*r - 2*gap - w]
        elif turn%2 == 1:
            o = 'W'
            meanders += halfarc_trench(r, w, gap, arccentre[0], arccentre[1], orient=o)
            remove += [halfarc(r - d_dots, w + 2*gap + 2*d_dots, arccentre[0], arccentre[1], orientation=o)]
            meanders += straight_trench(lmeander, gap, w, arccentre[0], arccentre[1] -r -2*gap - w)
            remove += [rect(lmeander, 2*gap + w + 2*d_dots, arccentre[0], arccentre[1] -r -2*gap - w - d_dots)]
            arccentre = [arccentre[0] + lmeander, arccentre[1] - 2*r - 2*gap - w]
    tail_shapes = []
    fine_shapes = []
    if tail == True:
        if nturns%2 == 0:
            o = 'NE'
        elif nturns%2 == 1:
            o = 'NW'
        if constriction == True:
            tail_shapes += quarterarc_trench(r, w, gap, arccentre[0], arccentre[1], orient=o)
            remove += [quarterarc(r - d_dots, 2*gap + w + 2*d_dots, arccentre[0], arccentre[1], orientation=o)]
            if o =='NE':
                fine_shapes += straight_trench(ltail*constrictionr, gap + float(w - constrictionw)/2, constrictionw, arccentre[0] + r, arccentre[1] -  ltail*constrictionr - w - spacer, orientation='V')
                fine_shapes += straight_trench(spacer, gap, w, arccentre[0] + r, arccentre[1] - spacer, orientation='V')
                fine_shapes += thinning_trench(w, constrictionw, gap, arccentre[0] + r, arccentre[1] - w  - spacer)
                fine_shapes += thinning_trench(constrictionw, w, gap, arccentre[0] + r, arccentre[1] - w - ltail*constrictionr  - spacer)
                fine_shapes += straight_trench(ltail*(1-constrictionr), gap, w, arccentre[0] + r, arccentre[1] -  ltail - 2*w  - spacer, orientation='V')
                remove += [rect(2*gap + w + 2*d_dots, ltail + spacer + 2*w + d_dots, arccentre[0] + r - d_dots, arccentre[1] -  ltail - 2*w  - spacer - d_dots)]
                # if SQUID == True:
                #     fine_shapes += straight_trench(squid_loop, (w - squid_loop - 2*constriction)/2., w - (w - squid_loop - 2*constriction), squid_loop, arccentre[0] + r, arccentre[1] -  ltail - 2*w  - spacer + squid_loop, orientation='V')
                #     fine_shapes += rect(squid_loop, squid_loop, arccentre[0] + r + gap + w/2 - squid_loop/2, arccentre[1] -  ltail - 2*w  - spacer + squid_loop)
            elif o =='NW':
                fine_shapes += straight_trench(ltail*constrictionr, gap + float(w - constrictionw)/2, constrictionw, arccentre[0] - r - 2*gap -w, arccentre[1] -  ltail*constrictionr - w  - spacer, orientation='V')
                fine_shapes += straight_trench(spacer, gap, w, arccentre[0] - r - 2*gap -w, arccentre[1] - spacer, orientation='V')
                fine_shapes += thinning_trench(w, constrictionw, gap, arccentre[0] - r - 2*gap -w, arccentre[1] - w  - spacer)
                fine_shapes += thinning_trench(constrictionw, w, gap, arccentre[0] - r - 2*gap -w, arccentre[1] - w - ltail*constrictionr  - spacer)
                fine_shapes += straight_trench(ltail*(1-constrictionr), gap, w, arccentre[0] - r - 2*gap -w, arccentre[1] -  ltail- 2*w  - spacer, orientation='V')
                remove += [rect(2*gap + w + 2*d_dots, ltail + spacer + 2*w + d_dots, arccentre[0] - r - 2*gap -w - d_dots, arccentre[1] -  ltail- 2*w  - spacer - d_dots)]
                # if SQUID == True:
                #     fine_shapes += straight_trench(squid_loop, (w - squid_loop - 2*constriction)/2., w - (w - squid_loop - 2*constriction), squid_loop, arccentre[0] - r - 2*gap -w, arccentre[1] -  ltail - 2*w  - spacer + squid_loop, orientation='V')
                #     fine_shapes += rect(squid_loop, squid_loop, arccentre[0] - r - 2*gap -w + gap + w/2 - squid_loop/2, arccentre[1] -  ltail - 2*w  - spacer + squid_loop)
        else:
            tail_shapes += quarterarc_trench(r, w, gap, arccentre[0], arccentre[1], orient=o)
            remove += [quarterarc(r - d_dots, 2*gap + w + 2*d_dots, arccentre[0], arccentre[1], orientation=o)]
            if o =='NE':
                if SQUID == True:
                    fine_shapes += [rect()]
                fine_shapes += straight_trench(ltail, gap, w, arccentre[0] + r, arccentre[1] - ltail, orientation='V')
                remove += [rect(2*gap + w + 2*d_dots, ltail + d_dots, arccentre[0] + r - d_dots,  arccentre[1] -  ltail - d_dots)]
            elif o =='NW':
                if SQUID == True:
                    fine_shapes += [rect(SQUID_r*w, SQUID_H, arccentre[0] - r - gap -w + .5*(w - w*SQUID_r), arccentre[1] - ltail + 10)]
                    fine_shapes += straight_trench(SQUID_con_H, .25*(w -SQUID_r*w -  2*SQUID_constriction), SQUID_constriction, arccentre[0] - r - gap -w, arccentre[1] - ltail + 10 + 0.5*SQUID_H, orientation='V')
                    fine_shapes += straight_trench(SQUID_con_H, .25*(w -SQUID_r*w -  2*SQUID_constriction), SQUID_constriction, arccentre[0] - r - gap + .5*(-w +SQUID_r*w), arccentre[1] - ltail + 10 + 0.5*SQUID_H, orientation='V')
                fine_shapes += straight_trench(ltail, gap, w, arccentre[0] - r - 2*gap -w, arccentre[1] - ltail, orientation='V')
                remove += [rect(2*gap + w + 2*d_dots, ltail + d_dots, arccentre[0] - r - d_dots- 2*gap -w,  arccentre[1] -  ltail - d_dots)]


    else:
        pass
    cap = [move(i, 0, -2*gap - w) for i in cap]
    meanders = [move(i, 0, -2*gap - w) for i in meanders]
    tail_shapes = [move(i, 0, -2*gap - w) for i in tail_shapes]
    fine_shapes = [move(i, 0, -2*gap - w) for i in fine_shapes]
    remove = [move(i, 0, -2*gap -w) for i in remove]
    if flip_y == 'True':
        cap = [flip(i) for i in cap]
        meanders = [flip(i) for i in meanders]
        tail_shapes = [flip(i) for i in tail_shapes]
        fine_shapes = [flip(i) for i in fine_shapes]
        remove = [flip(i) for i in remove]
    return [cap + meanders + tail_shapes, fine_shapes, remove]

def antidot_array(x0, y0, X, Y, w, s, n):
    return [[(ii*(s + w) + x0, jj*(s + w) + y0), (ii*(s + w) + w + x0, jj*(s + w) + y0),
               (ii*(s + w) + w + x0, jj*(s + w) + w + y0), (ii*(s + w) + x0, jj*(s + w) + w + y0)]
               for ii in np.arange(-n, X/(s+w) + n, 1)
               for jj in np.arange(-n, Y/(s+w) + n, 1)]

def feedline(cc, rat, r, W, H, bond, d_dots):
    #deltaL
    dL = [rect(bond*(1 + 2*rat), bond*rat, 0, 0)]
    dL += straight_trench(bond, bond*rat, bond, 0, bond*rat, orientation='V')
    dL += thinning_trench_style_2(bond, cc, rat, 0, bond*(1+rat), bond)

    #deltaR
    dR = [rect(bond*(1 + 2*rat), bond*rat, cc*(1 + 2*rat) + W + 2*r, 0)]
    dR += straight_trench(bond, bond*rat, bond, cc*(1 + 2*rat) + W + 2*r, bond*rat, orientation='V')
    dR += thinning_trench_style_2(bond, cc, rat, cc*(1 + 2*rat) + W + 2*r, bond*(1+rat), bond)

    #narrow - shapes start on left and move along feedline
    narrow = straight_trench(H, cc*rat, cc, bond*(rat + .5) - cc*(rat + .5), bond*(2 + rat), orientation='V')
    narrow += quarterarc_trench(r, cc, cc*rat, r+ bond*(rat + .5) + cc*(rat + .5), bond*(2 + rat) + H, orient='NW')
    narrow += straight_trench(W, cc*rat, cc, r+ bond*(rat + .5) + cc*(rat + .5), bond*(2 + rat) + H + r, orientation='H')
    narrow += quarterarc_trench(r, cc, cc*rat, r+ W + bond*(rat + .5) + cc*(rat + .5) , bond*(2 + rat) + H, orient='NE')
    narrow += straight_trench(H, cc*rat, cc, bond*(rat + .5) + cc*(rat + .5) + W + 2*r, bond*(2 + rat), orientation='V')

    #shapes to remove antidots from
    #dl
    remove = [rect(bond*(1 + 2*rat) + 2*d_dots, bond*(rat + 1) + d_dots, -d_dots , -d_dots)]
    remove += [[(-d_dots, bond*(rat + 1)), (bond*(1 + 2*rat) + d_dots, bond*(rat + 1)), (bond*(rat + .5) + cc*(rat + .5) + d_dots, bond*(rat + 2)), (bond*(rat + .5) - cc*(rat + .5) - d_dots, bond*(rat + 2))]]

    #dr
    remove += [rect(bond*(1 + 2*rat) + 2*d_dots,  bond*(rat + 1) + d_dots, cc*(1 + 2*rat) + W + 2*r -d_dots, -d_dots)]
    remove += [[(cc*(1 + 2*rat) + W + 2*r - d_dots, bond*(rat + 1)), (d_dots + cc*(1 + 2*rat) + W + 2*r + bond*(1 + 2*rat), bond*(rat + 1)), (d_dots + cc*(1 + 2*rat) + W + 2*r + bond*(rat + .5) + cc*(rat + .5), bond*(rat + 2)), (cc*(1 + 2*rat) + W + 2*r +bond*(rat + .5) - cc*(rat + .5) - d_dots, bond*(rat + 2))]]

    #narrow quarterarc(r, w, x0, y0, orientation='NE')
    remove += [rect(cc*(1 + 2*rat) + 2*d_dots, H, bond*(rat + .5) - cc*(rat + .5) - d_dots, bond*(2 + rat))]
    remove += [quarterarc(r - d_dots, cc*(1 + 2*rat) + 2*d_dots, r+ bond*(rat + .5) + cc*(rat + .5), bond*(2 + rat) + H, orientation='NW')]
    remove += [rect(W, cc*(1 + 2*rat) + 2*d_dots, r+ bond*(rat + .5) + cc*(rat + .5), bond*(2 + rat) + H + r - d_dots)]
    remove += [quarterarc(r - d_dots, cc*(1 + 2*rat) + 2*d_dots, r+ W + bond*(rat + .5) + cc*(rat + .5) , bond*(2 + rat) + H, orientation='NE')]
    remove += [rect(cc*(1 + 2*rat) + 2*d_dots, H, bond*(rat + .5) + cc*(rat + .5) + W + 2*r - d_dots, bond*(2 + rat))]

    return [dL + dR + narrow, remove]

def quarterwave_inverted(w, gap, nturns, lcap, lmeander, r, tail=True, ltail=100,
                constriction=True, constrictionw=1, constrictionr=.5, spacer=5,
                SQUID=True, squid_loop=2, squid_constriction=0.5,
                flip_y='True', npoints=16):
    '''
    List of list of list of tuples.
    There are two lists denoting different parts of the resonator. One list is
    the capacitor, meanders and part of the tail. Second list contains the fine
    shapes. This allows these to be saved to different laye
    '''
    remove = [rect(gap, 2*gap + w , 0, 0)]
    coarse = [rect(lcap, w, gap, gap)]
    remove += [rect(lcap, 2*(gap) + w, gap, 0)]
    coarse += [rect(lcap, w, gap, gap)]
    arccentre = [gap + lcap, -r]
    for turn in range(nturns):
        if turn%2 == 0:
            o = 'E'
            coarse += [halfarc(r + gap, w, arccentre[0], arccentre[1], orientation=o, npoints=npoints)]
            remove += [halfarc(r, w + 2*gap, arccentre[0], arccentre[1], orientation=o, npoints=npoints)]
            coarse += [rect(lmeander, w, arccentre[0] - lmeander, arccentre[1] - r - gap - w)]
            remove += [rect(lmeander, 2*gap + w, arccentre[0] - lmeander, arccentre[1] - r - 2*gap - w)]
            arccentre = [arccentre[0] - lmeander, arccentre[1] - 2*r - 2*gap - w]
        elif turn%2 == 1:
            o = 'W'
            coarse += [halfarc(r + gap, w, arccentre[0], arccentre[1], orientation=o, npoints=npoints)]
            remove += [halfarc(r , w + 2*gap, arccentre[0], arccentre[1], orientation=o, npoints=npoints)]
            coarse += [rect(lmeander, w,arccentre[0], arccentre[1] -r -gap - w)]
            remove += [rect(lmeander, 2*gap + w , arccentre[0], arccentre[1] -r -2*gap - w )]
            arccentre = [arccentre[0] + lmeander, arccentre[1] - 2*r - 2*gap - w]
    fine = []
    if tail == True:
        if nturns%2 == 0:
            o = 'NE'
        elif nturns%2 == 1:
            o = 'NW'
        if constriction == True:
            coarse += [quarterarc(r + gap, w, arccentre[0], arccentre[1], orientation=o, npoints=npoints)]
            remove += [quarterarc(r , 2*gap + w , arccentre[0], arccentre[1], orientation=o, npoints=npoints)]
            if o =='NE':
                fine += [rect(w, ltail*constrictionr, arccentre[0] + r + gap, arccentre[1] -  ltail*constrictionr - spacer)]
                #fine_shapes += straight_trench(ltail*constrictionr, gap + float(w - constrictionw)/2, constrictionw, arccentre[0] + r, arccentre[1] -  ltail*constrictionr - w - spacer, orientation='V')
                fine += [rect(w, spacer, arccentre[0] + r + gap, arccentre[1] - spacer)]
                #fine_shapes += straight_trench(spacer, gap, w, arccentre[0] + r, arccentre[1] - spacer, orientation='V')
                fine += [[(arccentre[0] + r + gap, arccentre[1] - spacer - ltail*constrictionr), (arccentre[0] + r + gap + w, arccentre[1] - spacer - ltail*constrictionr), (arccentre[0] + r + gap + w*.5 + constrictionw*.5, arccentre[1] - spacer - (w - constrictionw)*.5  - ltail*constrictionr), (arccentre[0] + r + gap + w*.5 - constrictionw*.5,arccentre[1] - spacer - (w - constrictionw)*.5 - ltail*constrictionr)]]
                #fine_shapes += thinning_trench(w, constrictionw, gap, arccentre[0] + r, arccentre[1] - w  - spacer)
                fine += [[(arccentre[0] + r + gap + w*.5 - constrictionw*.5, arccentre[1] - spacer - ltail), (arccentre[0] + r + gap + w*.5 + constrictionw*.5, arccentre[1] - spacer - ltail), (arccentre[0] + r + gap + w, arccentre[1] - spacer - (w - constrictionw)*.5 - ltail), (arccentre[0] + r + gap,arccentre[1] - spacer - (w - constrictionw)*.5 - ltail)]]
                #fine_shapes += thinning_trench(constrictionw, w, gap, arccentre[0] + r, arccentre[1] - w - ltail*constrictionr  - spacer)
                fine += [rect(constrictionw, ltail*(1-constrictionr), arccentre[0] + r + gap + .5*(w - constrictionw), arccentre[1] - spacer - ltail*(1-constrictionr))]
                #fine_shapes += straight_trench(ltail*(1-constrictionr), gap, w, arccentre[0] + r, arccentre[1] -  ltail - 2*w  - spacer, orientation='V')
                remove += [rect(2*gap + w , ltail + spacer + 2*w , arccentre[0] + r, arccentre[1] -  ltail - 2*w  - spacer)]
                print("even number of turns in res cst not well tested")
                # if SQUID == True:
                #     fine_shapes += straight_trench(squid_loop, (w - squid_loop - 2*constriction)/2., w - (w - squid_loop - 2*constriction), squid_loop, arccentre[0] + r, arccentre[1] -  ltail - 2*w  - spacer + squid_loop, orientation='V')
                #     fine_shapes += rect(squid_loop, squid_loop, arccentre[0] + r + gap + w/2 - squid_loop/2, arccentre[1] -  ltail - 2*w  - spacer + squid_loop)
            elif o =='NW':
                fine += [rect(w, ltail*constrictionr, arccentre[0] - r - gap -w, arccentre[1] -  ltail*constrictionr - spacer)]
                # fine_shapes += straight_trench(ltail*constrictionr, gap + float(w - constrictionw)/2, constrictionw, arccentre[0] - r - 2*gap -w, arccentre[1] -  ltail*constrictionr - w  - spacer, orientation='V')
                fine += [rect(w, spacer,arccentre[0] - r - gap -w, arccentre[1] - spacer)]
                # fine_shapes += straight_trench(spacer, gap, w, arccentre[0] - r - 2*gap -w, arccentre[1] - spacer, orientation='V')
                fine += [[(arccentre[0] - r - gap -w, arccentre[1] -  ltail*constrictionr - spacer), (arccentre[0] - r - gap , arccentre[1] -  ltail*constrictionr  - spacer), (arccentre[0] - r - gap - 0.5*(w - constrictionw), arccentre[1] -  ltail*constrictionr  - spacer- (w - constrictionw)*.5), (arccentre[0] - r - gap - 0.5*(w + constrictionw), arccentre[1] -  ltail*constrictionr  - spacer- (w - constrictionw)*.5)]]
                fine += [[(arccentre[0] - r - gap - 0.5*(w + constrictionw), arccentre[1] -  ltail - w  - spacer + 0.5*(w + constrictionw)), (arccentre[0] - r - gap - 0.5*(w - constrictionw) , arccentre[1] -  ltail - w  - spacer + 0.5*(w + constrictionw)), (arccentre[0] - r - gap, arccentre[1] -  ltail - w  - spacer + constrictionw), (arccentre[0] - r - gap -w, arccentre[1] -  ltail - w  - spacer + constrictionw)]]
                #fine_shapes += thinning_trench(w, constrictionw, gap, arccentre[0] - r - 2*gap -w, arccentre[1] - w  - spacer)
                # fine_shapes += thinning_trench(constrictionw, w, gap, arccentre[0] - r - 2*gap -w, arccentre[1] - w - ltail*constrictionr  - spacer)
                fine += [rect(constrictionw, ltail*(1-constrictionr), arccentre[0] - r - gap -0.5*(w + constrictionw) , arccentre[1] -  ltail - w  - spacer + 0.5*(w + constrictionw))]
                # fine_shapes += straight_trench(ltail*(1-constrictionr), gap, w, arccentre[0] - r - 2*gap -w, arccentre[1] -  ltail- 2*w  - spacer, orientation='V')
                fine += [rect(w, w + constrictionw, arccentre[0] - r - gap - w, arccentre[1] -  ltail- 2*w  - spacer)]
                remove += [rect(2*gap + w, ltail + spacer + 2*w, arccentre[0] - r - 2*gap -w , arccentre[1] -  ltail- 2*w  - spacer )]
                # if SQUID == True:
                #     fine_shapes += straight_trench(squid_loop, (w - squid_loop - 2*constriction)/2., w - (w - squid_loop - 2*constriction), squid_loop, arccentre[0] - r - 2*gap -w, arccentre[1] -  ltail - 2*w  - spacer + squid_loop, orientation='V')
                #     fine_shapes += rect(squid_loop, squid_loop, arccentre[0] - r - 2*gap -w + gap + w/2 - squid_loop/2, arccentre[1] -  ltail - 2*w  - spacer + squid_loop)
        else:
            print("You need to update res_shapes to include this without \
                fine shapes. You can probably hack this by setting the widths \
                of the constriction and the central conductor to being the \
                same. Past Oscar didn't test this. Sorry.")
            # coarse += quarterarc(r + gap, w, gap, arccentre[0], arccentre[1], orientation=o)
            # if o =='NE':
            #     ail_shapest += straight_trench(ltail, gap, w, arccentre[0] + r, arccentre[1] - ltail, orientation='V')
            # elif o =='NW':
            #     tail_shapes += straight_trench(ltail, gap, w, arccentre[0] - r - 2*gap -w, arccentre[1] - ltail, orientation='V')


    else:
        pass
    coarse = [move(i, 0, -2*gap - w) for i in coarse]
    fine = [move(i, 0, -2*gap - w) for i in fine]
    remove = [move(i, 0, -2*gap -w) for i in remove]
    if flip_y == 'True':
        coarse = [flip(i) for i in coarse]
        fine = [flip(i) for i in fine]
        remove = [flip(i) for i in remove]
    return [coarse, fine, remove]

def hw_sim(cc, gap, r, lcap, lstart, c_gap, npts=16):
    #arm in
    shapes = [rect(lcap, cc, 0, 0)]
    shapes += [rect(lstart, cc, lcap+c_gap, 0)]
    remove = [rect(lcap + lstart + c_gap, cc + 2*gap, 0, -gap)]
    #turn down
    shapes += [quarterarc(r, cc, lcap + lstart + c_gap, - r, orientation='NE', npoints=npts)]
    remove += [quarterarc(r - gap, cc + 2*gap, lcap + lstart + c_gap, - r, orientation='NE', npoints=npts)]
    #half arc back up
    shapes += [halfarc(r, cc, lcap + lstart + c_gap + cc + 2*r, -r, orientation='S', npoints=npts)]
    remove += [halfarc(r - gap, cc + 2*gap, lcap + lstart + c_gap + cc + 2*r, -r, orientation='S', npoints=npts)]
    #middle vertical
    shapes += [rect(cc, 2*r, lcap + lstart + c_gap + cc + 3*r, -r)]
    remove += [rect(cc + 2*gap, 2*r, lcap + lstart + c_gap + cc + 3*r - gap, -r)]
    #half arc back down
    shapes += [halfarc(r, cc, lcap + lstart + c_gap + 2*cc + 4*r, r, orientation='N', npoints=npts)]
    remove += [halfarc(r - gap, cc + 2*gap, lcap + lstart + c_gap + 2*cc + 4*r, r, orientation='N', npoints=npts)]
    #turn to horizontal
    shapes += [quarterarc(r, cc, lcap + lstart + c_gap + 3*cc + 6*r, r, orientation='SW', npoints=npts)]
    remove += [quarterarc(r - gap, cc + 2*gap, lcap + lstart + c_gap + 3*cc + 6*r, r, orientation='SW', npoints=npts)]
    #arm out
    shapes += [rect(lcap, cc, lcap + lstart + c_gap + 3*cc + 6*r + lstart + c_gap, -cc)]
    shapes += [rect(lstart, cc, lcap + lstart + c_gap + 3*cc + 6*r, -cc)]
    remove += [rect(lcap + lstart + c_gap, cc + 2*gap, lcap + lstart + c_gap + 3*cc + 6*r, -gap - cc)]
    L = 2*lcap + 2*lstart + 2*c_gap + 3*cc + 6*r
    H = 2*(2*r + cc + gap)
    return [shapes, remove, L, H]

def alignment_mark(x0,y0,w,l):
    x0=float(x0)
    y0=float(y0)
    shapes = []
    shapes += [rect(l, w, x0 + .55*w , y0-.5*w)]
    shapes += [rect(l, w, x0 - .55*w-l, y0-.5*w)]
    shapes += [rect(w, l, x0 - .5*w, y0+.55*w )]
    shapes += [rect(w, l, x0 - .5*w, y0-.55*w - l)]
    shapes += [rect(.45*w,.45*w,x0-.5*w, y0-.5*w)]
    shapes += [rect(.45*w,.45*w,x0-.5*w, y0 +.05*w)]
    shapes += [rect(.45*w,.45*w,x0 +.05*w, y0 -.5*w)]
    shapes += [rect(.45*w,.45*w,x0 + .05*w, y0+.05*w)]
    shapes += [rect(.05, .05, x0-.025, y0-.025)]
    return shapes
