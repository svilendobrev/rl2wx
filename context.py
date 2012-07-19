#$Id: context.py 8436 2009-04-27 09:46:29Z hristo $


import wx
from graphix_dc import GraphicsDC, wx_color
from adapter_gc import AdapterGC


class Context( object):
    ''' Defines a uniform interface for drawing on various wx contexts and hides all
        the wx stuff from clients.'''
    DEBUG = 0

    USE_RASTER_GRAPHICS = 0

    cap_mode_translator = {
        0 : wx.CAP_BUTT,
        1 : wx.CAP_ROUND,
        2 : wx.CAP_PROJECTING,
    }

    fill_styles = {
        0 : wx.TRANSPARENT,
        1 : wx.SOLID,
    }

    join_mode_translator = {
        0 : wx.JOIN_MITER,
        1 : wx.JOIN_ROUND,
        2 : wx.JOIN_BEVEL,
    }

    fill_rules = {
        0 : wx.ODDEVEN_RULE,
        1 : wx.WINDING_RULE,
    }

    def __init__( me, dc):
        if me.USE_RASTER_GRAPHICS and isinstance( dc, wx.WindowDC):
            me.context = AdapterGC( dc)
        else:
            me.context = GraphicsDC( dc)
        dpi = me.context.GetPPI()
        if me.DEBUG:
            print 'mapmode was:', me.context.GetMapMode(), 'dpi:', dpi, ' now set to MM_POINTS'
        me.context.SetMapMode( wx.MM_POINTS)
#        me.context.SetMapMode( wx.MM_TEXT)#POINTS)

        me.context.SetAxisOrientation( True, True)
        import sys
        if 0 and sys.platform == 'win32':
            me.context.SetDeviceOrigin( 0, 1200)
        else:
            me.context.SetDeviceOrigin( 0, me.context.GetSize().y-1)
        #me.context.SetLogicalOrigin( 0, 0)

        if me.DEBUG:
            me.context.DrawLine( 0,10, 200, 10)
            me.context.DrawLine( 0,840, 100,840)

        if me.DEBUG:
            me.context.DrawLine( 0,0, 50,100)

    def SetPen( me, rgb, width, line_dash =None, line_cap =0, line_join =0, style =1):
        pen = me.context.state.pen_data
        pen.colour  = wx_color( *rgb)
        pen.cap     = me.cap_mode_translator[ line_cap]
        pen.join    = me.join_mode_translator[ line_join]
        pen.width   = width
        pen.dashes  = line_dash
        pen.style   = me.fill_styles[ style]

        me.context._update_context()

    def SetBrush( me, rgb, style, fill_rule =0):
        #me.context.state.fill_rule = me.fill_rules[ fill_rule]
        color = wx_color( *rgb)

        fill_style = me.fill_styles[ style]
        brush = wx.TheBrushList.FindOrCreateBrush( color, fill_style)
        me.context.SetBrush( brush)
        me.context.SetTextForeground( color)

    def SetFont( me, face_name, point_size, bold =False, italic =False, underline =False):
        font = wx.TheFontList.FindOrCreateFont( point_size, wx.DEFAULT, wx.NORMAL, wx.NORMAL, underline, face_name)
        if bold:
            font.SetWeight( wx.BOLD)
        if italic:
            font.SetStyle( wx.ITALIC)
        me.context.SetFont( font)

    def DrawPath( me, path, stroke=1, fill=0, fill_rule=0):
        # FIXME problems with FindOrCreatePen, as it seems we must work with
        # a single pen and modify it as needed instead of creating new one each time

        me.PushState()
        #me.context.state.fill_rule = me.fill_rules[ fill_rule]
        if not fill:
            me.SetBrush( (255,255,255), 0)
        if not stroke:
            pen = wx.ThePenList.FindOrCreatePen( wx_color('WHITE'), 1, wx.TRANSPARENT)
            me.context.SetPen( pen)
        path.recorder.DEBUG = me.DEBUG
        path.recorder.play_on( me)
        me.PopState()

    def ClipPath( me, path, stroke=1, fill=0, fill_rule=0):
        raise NotImplementedError

    def SetTextForeground( me, r, g, b):
        me.context.SetTextForeground( wx_color( r, g, b))

    def SetTextBackground( me, r, g, b):
        me.context.SetTextBackground( wx_color( r, g, b))

    def DrawTextObject( me, textobj):
        textobj.recorder.DEBUG = me.DEBUG
        textobj.recorder.play_on( me)

    def __getattr__( me, name):
        return getattr( me.context, name)

# vim:ts=4:sw=4:expandtab
