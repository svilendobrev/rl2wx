#$Id: page_recorder.py 8436 2009-04-27 09:46:29Z hristo $
# -*- coding: cp1251 -*-

from recorder import Recorder
class Page( Recorder):
    ''' Records all operations needed to draw a single page '''
    def __init__( me, width, height, rec_context):
        Recorder.__init__( me, rec_context)
        me.width = width
        me.height = height

    def __str__( me):
        s = 'Page size=(%s, %s)\n' % (str(me.width), str(me.height))
        s += '\n'.join( str(call) for call in me.method_calls)
        return s


import wx

class PageRecorder( object):
    ''' Records the whole drawing process segmented into pages.'''
    DEBUG = 0

    def __init__( me, pagesize):
        me.pages = []
        me._create_page( *pagesize)

    def get_pagesize( me, page_idx):
        if me.pages:
            page = me.pages[ page_idx]
            return page.width, page.height
        return None

    def new_page( me, w, h):
        me.pages.append( me.current_page)
        me._create_page( w, h)
        if me.DEBUG:
            print 'drawing at page', len(me.pages)

    def draw_page( me, page_idx, dc):
        from context import Context
        page = me.pages[ page_idx]
        page.DEBUG = me.DEBUG

        use_buffer = 0 and isinstance( dc, wx.WindowDC)
        if use_buffer:
            buff_dc = wx.MemoryDC()
            buff_bmp = wx.EmptyBitmap( page.width, page.height)
            buff_dc.SelectObject( buff_bmp)

            if not buff_dc.IsOk():
                print 'ERROR: cant create a buffer to draw in'
            context = Context( buff_dc)
            context.SetBrush( (255,255,255), wx.SOLID)
            context.DrawRectangle( 0,0, 400,400)
        else:
            context = Context( dc)

        #print page
        page.play_on( context)

        if use_buffer:
            dc.Blit( 0, 0, page.width, page.height, buff_dc, 0, 0)
            buff_dc.SelectObject( wx.NullBitmap)

    def _create_page( me, w, h):
        from context import Context
        if me.DEBUG:
            print '_create_page: ', w, h
        if 0*'PLAYwhileREC':
            from measure import point2pix
            buff = wx.EmptyBitmap( point2pix(w), point2pix(h))
            buff_dc = wx.MemoryDC( buff)
            context = Context( buff_dc)
        else:
            context = None
        me.current_page = Page( w, h, context)

    def __getattr__( me, name):
        return getattr( me.current_page, name)


if __name__ == '__main__':
    DRAW_PAGE_NUM = 0
    BUFFERED = 1

    def draw( rec):
        #first page
        rec.SetBrush( (255,100,255), 1)
        rec.DrawRectangle(110,310,300,300)
        rec.SetBrush( (0,255,0), 1)
        rec.DrawRectangle(0,0,200,200)
        rec.SetPen( (0,0,0), 10, line_join=2)
        rec.new_page( 300,300)

        #second page
        rec.SetPen( (0,0,0), 10, line_cap=2, line_join=0)
        rec.DrawLine(20,20,100,20)
        rec.DrawLine(100,20,100,100)
        rec.new_page( 300,300)
        print 'result:', rec.pages

    class TestWindow(wx.Panel):
        def __init__(me,parent, id):
            wx.Panel.__init__(me,parent,id)
            me.maxWidth  = 1000
            me.maxHeight = 1000

            if BUFFERED:
                me.buffer = wx.EmptyBitmap(me.maxWidth, me.maxHeight)
                dc = wx.BufferedDC(None, me.buffer)
                dc.SetBackground(wx.Brush(me.GetBackgroundColour()))
                dc.Clear()
                me.DoDrawing(dc)
            me.Bind(wx.EVT_PAINT, me.OnPaint)

        def OnPaint(me,evt):
            if BUFFERED:
                dc = wx.BufferedPaintDC(me, me.buffer, wx.BUFFER_VIRTUAL_AREA)
            else:
                dc = wx.PaintDC(me)
                me.PrepareDC(dc)
                me.DoDrawing(dc)

        def DoDrawing(me, dc):
            rec = PageRecorder( (1000,1000))
            draw( rec)

            dc.BeginDrawing()
            rec.draw_page( DRAW_PAGE_NUM, dc)
            dc.EndDrawing()


    app=wx.PySimpleApp()
    frame=wx.Frame(None, wx.ID_ANY,title="TEST GC",size=(800,600))
    win=TestWindow(frame, wx.ID_ANY)

    frame.Show()
    app.MainLoop()


# vim:ts=4:sw=4:expandtab
