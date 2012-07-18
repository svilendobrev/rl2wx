#$Id: pathobject.py 8436 2009-04-27 09:46:29Z hristo $
# -*- coding: cp1251 -*-

from reportlab.pdfgen.pathobject import PDFPathObject
from recorder import Recorder

class PathObject( PDFPathObject):
    def __init__( me):
        me.x = me.y = 0
        me.close_x = me.close_y = None
        me.recorder = Recorder()

    def getCode( me):
        return 'dummy replacement to keep it up to the original protocol'

    def _move_cursor( me, x, y):
        me.x, me.y = x, y

    def moveTo( me, x, y):
        ''' interrupts path by moving and sets new closing point'''
        me.close_x = x
        me.close_y = y
        me._move_cursor( x, y)

    # drawable without interruption
    def lineTo( me, x, y):
        me.recorder.DrawLine( me.x, me.y, x, y)
        me._move_cursor( x, y)

    def curveTo( me, x1, y1, x2, y2, x3, y3):
        me.recorder.DrawArc(  x1, y1, x2, y2, x3, y3)
        me._move_cursor( x2, y2)

    def arcTo( me, x1,y1, x2,y2, startAng=0, extent=90):
    #def AddArcToPoint( me, x1, y1, x2, y2, r):
        pass

    # path-interrupting ops
    def arc( me, x1,y1, x2,y2, startAng=0, extent=90):
        pass

    def rect( me, x, y, width, height):
        me.moveTo( x, y)
        me.recorder.DrawRectangle( x, y, width, height)

    def ellipse( me, x, y, width, height):
        me.recorder.DrawEllipse( x, y, width, height)
        me.moveTo( x, y)

    def circle( me, x_cen, y_cen, r):
        me.recorder.DrawCircle( x_cen, y_cen, r)
        me.moveTo( x_cen + r, y_cen)

    def close( me):
        ''' closes last uninterrupted part of path '''
        if me.close_x is not None and me.close_y is not None:
            me.lineTo( me.close_x, me.close_y)



# vim:ts=4:sw=4:expandtab
