#$Id: graphix_dc.py 8436 2009-04-27 09:46:29Z hristo $
# -*- coding: utf-8 -*-

import wx
from matrix import Matrix
import copy

to_int = lambda i: int( i+0.5)

def capitalize(s):
    if not s:
        return s
    return s[0].upper() + s[1:]

def wx_color( *args ):
    if len( args) > 1:
        return wx.Colour( *args)
    return wx.NamedColor( args[0])

############ State attributes
class StateAttribute( object):
    defaults = {}
    def __init__( me, **kargs):
        for name, vdefault in me.defaults.iteritems():
            val = kargs.get( name, vdefault)
            setattr( me, name, val)

    def copy(me):
        s = me.__class__()
        for name in me.defaults:
            setattr( s, name, getattr( me, name))
        return s

    def load_from_wx_obj( me, wxobj):
        for name in me.defaults:
            getter = getattr( wxobj, 'Get'+capitalize( name))
            setattr( me, name, getter())

class BrushSettings( StateAttribute):
    defaults = dict(
        colour   = wx_color('BLACK'),
        style   = wx.SOLID,
        #stipple = bitmap??
    )
    def make_wx_obj( me):
        return wx.TheBrushList.FindOrCreateBrush( me.colour, me.style)

class PenSettings( StateAttribute):
    defaults = dict(
        colour   = wx_color('BLACK'),
        width   = 1,
        cap     = wx.CAP_BUTT,
        join    = wx.JOIN_MITER,
        dashes  = [],
        style   = wx.SOLID
    )
    def make_wx_obj( me):
        if not me.dashes:
            style = wx.SOLID
        else:
            style = wx.USER_DASH # XXX crashes
        wxpen = wx.ThePenList.FindOrCreatePen( me.colour, me.width, me.style)
        wxpen.SetCap( me.cap)
        wxpen.SetJoin( me.join)
        if me.dashes:
            wxpen.SetDashes( me.dashes)
        return wxpen

class FontSettings( StateAttribute):
    defaults = dict(
        faceName    = '',
        family      = wx.SWISS,
        pointSize   = 14,
        weight      = wx.NORMAL,
        style       = wx.NORMAL,
        underlined  = False,
    )
    def make_wx_obj( me):
        return wx.TheFontList.FindOrCreateFont( me.pointSize, me.family, me.style,
                                                me.weight, me.underlined, me.faceName)


###########

class State( object):
    __slots__ = 'matrix pen_data brush_data font_data fill_rule text_foreground text_background'.split()
    def __init__( me, **kargs):
        for k,v in kargs.iteritems():
            setattr( me, k, v)
    def clone( me):
        s = me.__class__()
        for k in me.__slots__:
            item = getattr(me, k)
            copier = getattr( item, 'copy', None)
            if callable( copier):
                setattr( s, k, copier())
            else:
                setattr( s, k, item)
        return s


def scale_pen( func):
    '''Makes sure we always Push and Pop state when scaling pen width.
       This should decorate all methods that use pen while drawing.
    '''
    def scaled_pen_draw( me, *a, **ka):
        me.PushState()
        scale = min( me.state.matrix.transform_y_size( 1), me.state.matrix.transform_x_size( 1))
        me.state.pen_data.width *= scale
        me._update_context()
        res = func( me, *a, **ka)
        me.PopState()
        return res
    return scaled_pen_draw


class GraphicsDC( object):
    ''' Decorates wx.DC to behave like graphics state machine.
        Adds support for geometric transformations over graphics state matrix.
    '''

    DEBUG = 0

    @property
    def state( me):
        return me._state_stack[-1]

    def __init__( me, dc):
        me.context = dc
        me._state_stack = []

        me._state_attr_defaults = State(
            matrix      = Matrix(),
            pen_data    = PenSettings(),
            brush_data  = BrushSettings(),
            font_data   = FontSettings(),
            fill_rule   = wx.ODDEVEN_RULE,
            text_foreground = (0, 0, 0),
            text_background = (255, 255, 255),
        )

        me._state_stack.append( me._state_attr_defaults)
        me._update_context()

    def PushState( me):
        me._state_stack.append( me.state.clone())

    def PopState( me):
        me._state_stack.pop()
        me._update_context()

    # set methods
    def SetFont( me, font):
        me.state.font_data.load_from_wx_obj( font)
        me.context.SetFont( font)

    def SetPen( me, pen):
        me.state.pen_data.load_from_wx_obj( pen)
        me.context.SetPen( pen)

    def SetBrush( me, brush):
        me.state.brush_data.load_from_wx_obj( brush)
        me.context.SetBrush( brush)

    def SetTextForeground( me, colour):
        me.state.text_foreground = colour.Get()
        me.context.SetTextForeground( colour)

    def SetTextBackground( me, colour):
        me.state.text_background = colour.Get()
        me.context.SetTextBackground( colour)

    # draw methods
    @scale_pen
    def DrawLine( me, x1, y1, x2, y2):
        points=  me._transform_xy_int( x1, y1) + me._transform_xy_int( x2, y2)
        me.context.DrawLine( *points)

    @scale_pen
    def DrawRectangle( me, x, y, w, h):
        points = [ (x, y), (x+w,y), (x+w,y+h), (x,y+h) ]
        wxpoints = [ me._transform_xy_int( *p) for p in points ]
        me.context.DrawPolygon( wxpoints, fillStyle=me.state.fill_rule)

    #def DrawCircle( me, x, y, r):

    def DrawText( me, txt, x, y):
        me._draw_text( txt, x, y)

    def DrawRotatedText( me, txt, x, y, angle_rads):
        me._draw_text( txt, x, y, angle_rads)

    def Scale( me, x, y):
        me.state.matrix.scale( x, y)

    def Transform( me, a, b, c, d, e, f):
        me.state.matrix.post_mult_tuple( a, b, c, d, e, f)

    def Translate( me, dx, dy):
        me.state.matrix.translate( dx, dy)

    def _update_context( me):
        state = me.state
        c = me.context
        c.SetBrush( state.brush_data.make_wx_obj())
        c.SetPen( state.pen_data.make_wx_obj()    )
        c.SetFont( state.font_data.make_wx_obj()  )
        c.SetTextForeground( wx_color( *state.text_foreground))
        c.SetTextBackground( wx_color( *state.text_background))

    def __getattr__( me, name):
        #print me, 'passing %s to context' % name
        return getattr( me.context, name)

    def _draw_text( me, txt, x, y, angle =0, base_y =0):
        from svd_util.ui.wxtxt import _
        txt = _(txt)
        #print '@@@@ draw text', type(txt), repr(txt)
        import sys
        # XXX FIXME dont know why PrinterDC is not consistent for linux/win32
        special_mode = isinstance( me.context, wx.PrinterDC) and sys.platform == 'win32'

        if special_mode:
            dpi_pixels = me.context.GetPPI()
            dpi = [
                    me.context.DeviceToLogicalXRel( dpi_pixels[0]),
                    me.context.DeviceToLogicalYRel( dpi_pixels[1]),
                  ]
        else:
            dpi = me.context.GetPPI()

        if me.DEBUG:
            d = {
                wx.MM_TWIPS     : 'Each logical unit is 1/20 of a point, or 1/1440 of an inch.',
                wx.MM_POINTS    : 'Each logical unit is a point, or 1/72 of an inch.',
                wx.MM_METRIC    : 'Each logical unit is 1 mm.',
                wx.MM_LOMETRIC  : 'Each logical unit is 1/10 of a mm.',
                wx.MM_TEXT      : 'Each logical unit is 1 pixel.',
            }
            print 'mapmode:', d[ me.context.GetMapMode()], 'dpi:', dpi
            print me.context.LogicalToDeviceYRel(1000.0)

        me.PushState()
        matr = me.state.matrix
        matr.translate( x, y, pre=True)

        if angle:
            matr.rotate( angle, pre=True)

        dx, dy, descent, ext_leading = me.context.GetFullTextExtent( txt)
        #print 'fontmetrics', dx, dy, descent, ext_leading
        dy -= descent #get to the baseline
        #86: dpy[y]; xdpyinfo | grep resolution
        coef = 72.0/dpi[1] #0.75 ????  72/86 = 0.837
        #друга причина може да е _какво_ е 14пт - bbox.h или височината dy-descent?
        dx *= coef
        dy *= coef
        descent *= coef
        #print 'fontmetrics', dx, dy, descent, ext_leading

        scale = matr.transform_y_size( 1)
        if me.DEBUG:
            print 'scale' , scale
        #ext = scale * base_y
        if base_y:
            scale *= float( base_y) / dy
        else:
            base_y = dy

        font = me.context.GetFont()
        point_size = font.GetPointSize()
        scaled_point_size = point_size * scale * coef

        if 0: #'linux' in sys.platform:
            if 0:
                from reportlab.pdfbase.pdfmetrics import stringWidth
                font_data = me.state.font_data
                rl_width = stringWidth( txt, font_data.faceName, font_data.pointSize)
                wx_width = me.context.GetTextExtent( txt)[0]
                if not wx_width: wx_width = 1
                font_map_correction_coef = float(rl_width) / wx_width
            else:
                font_map_correction_coef = 0.8
            scaled_point_size *= font_map_correction_coef
        elif special_mode:
            # just to be sure it'll fit when we map different font from the one reportlab has used
            scaled_point_size *= 0.8
            fsize_pixels = font.GetPixelSize()
            fwidth, fheight = [
                me.context.DeviceToLogicalXRel( fsize_pixels[0]),
                me.context.DeviceToLogicalYRel( fsize_pixels[1])
            ]
            base_y += fheight
            if me.DEBUG:
                print 'In printer mode', base_y, 'h=', fheight, 'w=',fwidth, 'pix=', fsize_pixels

        font.SetPointSize( scaled_point_size)

        # XXX Why does not wx scale fonts when outputting to a pixel printer in windows ??
        # pixel_size = font.GetPixelSize()
        # font.SetPixelSize( pixel_size)
        me.context.SetFont( font)

        if me.DEBUG:
            print 'fontsize', point_size, 'scaled fontsize', scaled_point_size
            matrixbox = matr.copy()
            if 1*'fullbbox':
                dy += descent
                matrixbox.translate( 0, descent )
            pts = [ map( to_int, matrixbox.transform_xy( x, y))
                    for x,y in ((0,0), (dx,0), (dx,dy), (0,dy))
                  ]
            me.context.SetBrush( wx.Brush( wx.NamedColour('RED')))
            me.context.DrawPolygon( pts)

        p = me._transform_xy( 0, 0)
        q = me._transform_xy( dx, 0)
        from math import atan2, pi
        pangle = -180/pi * atan2( q[1]-p[1], q[0]-p[0])

        if 0:
            base_y = scaled_point_size - base_y + descent
        #print base_y
        #base_y -= 1 #??? закръглението требе да се обърне:-0.5 ЗА НЯКОИ неща ???
        matr.translate( 0, base_y, pre=True)

        p = me._transform_xy_int( 0,0)
        me.context.DrawRotatedText( txt, p[0], p[1], pangle)

        me.PopState()

    def _transform_xy( me, x, y, matrix =None):
        m = matrix or me.state.matrix
        return m.transform_xy( x,y)
    def _transform_xy_int( me, x, y, matrix =None):
        return [ to_int(c) for c in me._transform_xy( x,y, matrix) ]


if __name__ == '__main__':
    import unittest

    class TestDC( unittest.TestCase):
        def setUp( me):
            buff = wx.EmptyBitmap( 500,500)
            buff_dc = wx.MemoryDC( buff)
            me.context = GraphicsDC( buff_dc)

        def test_state_stack( me):
            depth = 10

            for i in range( 1, depth):
                me.assertEqual( i, len( me.context._state_stack), 'pushing')
                me.context.PushState()

            for i in range( depth, 1, -1):
                me.assertEqual( i, len( me.context._state_stack))#, 'poping')
                me.context.PopState()

            me.assertEqual( 1, len( me.context._state_stack))
            me.assertRaises( IndexError, me.context.PopState)


    import wx
    app = wx.PySimpleApp()
    unittest.main()

# vim:ts=4:sw=4:expandtab
