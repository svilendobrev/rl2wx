#$Id: matrix.py 8436 2009-04-27 09:46:29Z hristo $
# -*- coding: cp1251 -*-

from math import cos, sin, sqrt, atan2

def hypot2( x, y):
    return x*x + y*y

def hypot( x, y):
    return sqrt( hypot2( x, y))

def matrix_mult( A, B):
    a = A.a * B.a + A.b * B.c
    b = A.a * B.b + A.b * B.d
    c = A.c * B.a + A.d * B.c
    d = A.c * B.b + A.d * B.d
    e = A.e * B.a + A.f * B.c + B.e
    f = A.e * B.b + A.f * B.d + B.f
    return a, b, c, d, e, f


########################

class Matrix( object):
    ''' Graphics state matrix to perform affine transformations.
        It helps translate coordinates, scale, rotate and so on'''
    def __init__( me):
        me.set_identity()

    def set( me, a, b, c, d, e, f):
        me.a, me.b, me.c, me.d, me.e, me.f = a, b, c, d, e, f

    def det( me):
        return me.a * me.d - me.b * me.c

    def copy( me):
        new = me.__class__()
        new.set( *me.as_tuple())
        return new

    def as_tuple( me):
        return (getattr( me, name) for name in 'abcdef')

    def post_mult( me, M):
        res = matrix_mult( me, M)
        me.set( *res)

    def pre_mult( me, M):
        res = matrix_mult( M, me)
        me.set( *res)

    def post_mult_tuple( me, a, b, c, d, e, f):
        m = me.__class__()
        m.set( a, b, c, d, e, f)
        me.post_mult( m)

    def mult( me, M, pre =False):
        if pre:
            me.pre_mult( M)
        else:
            me.post_mult( M)

    # setup
    def set_identity( me):
        me.set( 1, 0, 0, 1, 0, 0)

    def set_invert( me, m):
        det = m.det()
        if det:
            me.a = m.d  / det
            me.b = -m.b / det
            me.c = -m.c / det
            me.d = m.a  / det
            me.e = (m.c * m.f - m.d * m.e) / det
            me.f = (m.b * m.e - m.a * m.f) / det
        return det

    def set_translate( me, dx, dy, pre =False):
        me.set( 1, 0, 0, 1, dx, dy)

    def set_scale( me, x, y):
        me.set( x, 0, 0, y, 0, 0)

    def set_translate_signed( me, matr):
        me.translate( matr.e, matr.f)
        if me.a < 0: me.a = -1
        if me.d < 0: me.d = -1

    def set_rotate( me, cosa, sina, center =None):
        if center:
            me.set_translate( -center[0], -center[1])
            me.rotate_cs( cosa, sina)
            me.translate( *center)
        else:
            me.set( cosa, sina, -sina, cosa, 0, 0)


    # transformations
    def transform_xy( me, x, y):
        xp = me.a*x + me.c*y + me.e
        yp = me.b*x + me.d*y + me.f
        return (xp, yp)

    def transform_x_size( me, size):
        x = me.transform_x_nooffs( size, 0)
        y = me.transform_y_nooffs( size, 0)
        return hypot( x, y)

    def transform_y_size( me, size):
        x = me.transform_x_nooffs( 0, size)
        y = me.transform_y_nooffs( 0, size)
        return hypot( x, y)

    def transform_x_nooffs( me, x, y):
        return x * me.a + y * me.c

    def transform_y_nooffs( me, x, y):
        return x * me.b + y * me.d

    def transform_x( me, x, y):
        return me.transform_x_nooffs( x, y) + me.e

    def transform_y( me, x, y):
        return me.transform_y_nooffs( x, y) + me.f

    def transform_angle( me, dx, dy):   pass
    def transform_angle2( me, angle):   pass

    # operations
    def translate( me, dx, dy, pre =False):
        if pre:
            matr = me.__class__()
            matr.set_translate( dx, dy)
            me.pre_mult( matr)
        else:
            me.e += dx
            me.f += dy

    def scale( me, x, y, pre =False):
        matr = me.__class__()
        matr.set_scale( x, y)
        me.mult( matr, pre)

    def rotate( me, angle, center =None, pre =False):
        me.rotate_cs( cos( angle), sin( angle), center, pre)

    def rotate_cs( me, cosa, sina, center =None, pre =False):
        matr = me.__class__()
        matr.set_rotate( cosa, sina, center)
        me.mult( matr, pre)

    def rotate_xy( me, x, y, center =None, pre =False):
        me.rotate( atan2( y, x), center, pre)

    ############### check funcs
    def is_identity_nooffs( me):
        return (me.a, me.b, me.c, me.d) == (1, 0, 0, 1)

    def is_identity( me):
        return me.is_identity() and (me.e, me.f) == (0, 0)

    def is_negating_angles( me):
        return me.det() < 0

    ###################

    def __str__( me):
        return 'matrix:' + ' '.join( str( getattr(me, n)) for n in 'abcdef')


# vim:ts=4:sw=4:expandtab
