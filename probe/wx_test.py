#$Id: wx_test.py 8436 2009-04-27 09:46:29Z hristo $
# -*- coding: cp1251 -*-

import wx

from reportlab.pdfbase import pdfmetrics

def replace_rl_stringWidth( dc):
    def wx_stringWidth(text, fontName, fontSize, encoding='utf8'):
        font = wx.TheFontList.FindOrCreateFont( fontSize, wx.SWISS, wx.NORMAL,
                                            wx.NORMAL, False, fontName)
        return dc.GetFullTextExtent( text, font)[0]
    pdfmetrics.stringWidth = wx_stringWidth
    import new
    pdfmetrics.Font.stringWidth = new.instancemethod( wx_stringWidth, None, pdfmetrics.Font)


app = wx.App()

from reportlab.lib.pagesizes import A4
dc = wx.MemoryDC()
buff_bmp = wx.EmptyBitmap( *A4 )
dc.SelectObject( buff_bmp)
dc.SetUserScale( 1.0, 1.0)

modes = {
    wx.MM_TWIPS     : 'MM_TWIPS    Each logical unit is 1/20 of a point, or 1/1440 of an inch.',
    wx.MM_POINTS    : 'MM_POINTS   Each logical unit is a point, or 1/72 of an inch.',
    wx.MM_METRIC    : 'MM_METRIC   Each logical unit is 1 mm.',
    wx.MM_LOMETRIC  : 'MM_LOMETRIC Each logical unit is 1/10 of a mm.',
    wx.MM_TEXT      : 'MM_TEXT     Each logical unit is 1 pixel.',
}

if 0:
    for mode in modes:
        dc.SetMapMode( mode)
        check_mode = dc.GetMapMode()
        assert check_mode == mode
        print '============ ', modes[ check_mode]
        check_funcs = 'GetSize GetSizeTuple GetSizeMM GetPPI'.split()
        for fname in check_funcs:
            print fname, getattr(dc, fname)()

        height_device = dc.GetSize().y
        print height_device, dc.DeviceToLogicalY( height_device)

        fontSize = 14
        fontName = 'ArialMT'
        font = wx.TheFontList.FindOrCreateFont( fontSize, wx.SWISS, wx.NORMAL,
                                            wx.NORMAL, False, fontName)
        print 'font', `font`
        dc.SetFont( font)

        print '------ extent'
        check_funcs = 'GetTextExtent GetFullTextExtent'.split()
        for fname in check_funcs:
            print fname, getattr(dc, fname)( 'ALABALA')[:2]

if 10:
    table_data = [ [ 10*'alabala' ] ]
    from reportlab.platypus.tables import LongTable, TableStyle
    from rl2wx.fonts import register_font
    print 'register font:', register_font('ArialMT')
    style_commands = [
        ('BOX', (0,0), (-1,-1), 1, 'BLACK'),
        ('FONTNAME', (0,0), (-1,-1), 'ArialMT'),
    ]
    style = TableStyle( style_commands )
    t = LongTable( data=table_data, style=style)
    from reporter.view.wx_view import make_pagerecorder
    pr = make_pagerecorder( [t], A4)
    from reporter.common import preview_recorder
    preview_recorder( pr)

app.MainLoop()


# vim:ts=4:sw=4:expandtab
