#$Id: adapter_gc.py 8436 2009-04-27 09:46:29Z hristo $


import wx

class AdapterGC( object):
    ''' wx.GraphicsContext implementation of Context interface'''
    def __init__( me, dc):
        me.context = wx.GraphicsContext.Create( dc)
        me._fill_rule = wx.ODDEVEN_RULE

    # set methods
    def SetFont( me, font):
        gfx_font = me.context.CreateFont( font)
        me.context.SetFont( gfx_font)

    def SetPen( me, pen):
        gfx_pen = me.context.CreatePen( pen)
        me.context.SetPen( gfx_pen)

    def SetBrush( me, brush):
        gfx_brush = me.context.CreateBrush( brush)
        me.context.SetBrush( gfx_brush)

    # draw methods
    def DrawLine( me, x1, y1, x2, y2):
        me.context.StrokeLine( x1, y1, x2, y2)

    def DrawCircle( me, x, y, r): pass

    def Transform( me, a, b, c, d, e, f):
        matr = me.context.CreateMatrix( a, b, c, d, e, f)
        me.context.ConcatTransform( matr)

    def CreatePath( me):
        path = me.context.CreatePath()
        from adapter_gc import PathGC
        return PathGC( path)

    def DrawPath( me, path):
        from adapter_gc import PathGC
        assert isinstance( path, PathGC)
        me.context.DrawPath( path.gfx_path, fillStyle=me._fill_rule)

    def __getattr__( me, name):
        return getattr( me.context, name)


##############################################


from reportlab.pdfgen.pathobject import PDFPathObject

class PathGC( PDFPathObject):
    def __init__( me, path):
        me.gfx_path = path

    def getCode( me):
        return 'dummy replacement to keep it up to the original protocol'

    def moveTo( me, x, y):
        me.gfx_path.MoveToPoint( x, y)

    def lineTo( me, x, y):
        me.gfx_path.AddLineToPoint( x, y)

    def curveTo( me, x1, y1, x2, y2, x3, y3):
        me.gfx_path.AddCurveToPoint( x1, x2, x2, y2, x3, y3)

    def arc( me, x1,y1, x2,y2, startAng=0, extent=90):
        """
        Draw a partial ellipse inscribed within the rectangle x1,y1,x2,y2,
        starting at startAng degrees and covering extent degrees.   Angles
        start with 0 to the right (+x) and increase counter-clockwise.
        These should have x1<x2 and y1<y2.

        The algorithm is an elliptical generalization of the formulae in
        Jim Fitzsimmon's TeX tutorial <URL: http://www.tinaja.com/bezarc1.pdf>."""
        #me.gfx_path.AddArc( x1, y1,  # TODO

    def arcTo( me, x1,y1, x2,y2, startAng=0, extent=90):
        """Like arc, but draws a line from the current point to
        the start if the start is not the current point."""
        # me.gfx_path.AddArcToPoint( x1, y1, x2, y2,  TODO

    def rect( me, x, y, width, height):
        me.gfx_path.AddRectangle( x, y, width, height)

    def ellipse( me, x, y, width, height):
        me.gfx_path.AddEllipse( x, y, width, height)

    def circle( me, x_cen, y_cen, r):
        me.gfx_path.AddCircle( x_cen, y_cen, r)

    def close( me):
        "draws a line back to where it started"
        me.gfx_path.CloseSubPath()


# vim:ts=4:sw=4:expandtab
