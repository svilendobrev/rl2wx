#$Id: test.py 8436 2009-04-27 09:46:29Z hristo $
# -*- coding: cp1251 -*-

import wx
from printout import MyPrintout

OUT2PDF = 0
inch = 72.0 #25.4

def draw_table( context, pagesize):
    from reportlab.platypus.doctemplate import SimpleDocTemplate
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib import colors
    from engine.rl2wx.canvas import Canvas

    if OUT2PDF:
        from reportlab.pdfgen.canvas import Canvas
        context = 'alabala.pdf'

    data = []
    for i in range(3):
        row = []
        for j in range(3):
            row.append( str(i)+str(j)+unicode('bp','cp1251'))
        data.append( row)

    widths = [ 20, None, None]
    table = Table( data, colWidths=widths)

    if 1:
        style = TableStyle(())

        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase import pdfmetrics
        from reportlab import rl_config
        rl_config.T1SearchPath.insert( 0, '/usr/share/fonts/X11/Type1/')
        pdfmetrics.dumpFontData()

        #pdfmetrics.registerFont( TTFont('TIMES', 'Verdana.ttf'))

        fontname = 'CharterBT-Roman'
        pdfmetrics.findFontAndRegister( fontname)

        style.add( 'FONTNAME', (0,0), (-1,-1), fontname, 84)
        style.add( 'FONTSIZE', (0,0), (-1,-1), 24)
        style.add( 'LEADING',  (0,0), (-1,-1), 24)
        style.add( 'BOX', (0,0), (-1,-1), 0.25, colors.black)
        style.add( 'INNERGRID', (0,0), (-1,-1), 0.25, colors.black)
        #style.add('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black)
        style.add('LINEBELOW', (0,-1), (-1,-1), 2, colors.green)

        style.add('LEFTPADDING'  , (0,0), (-1,-1), 0)
        style.add('RIGHTPADDING' , (0,0), (-1,-1), 0)
        style.add('BOTTOMPADDING', (0,0), (-1,-1), 0)
        style.add('TOPPADDING'   , (0,0), (-1,-1), 0)

        table.setStyle( style)

    story = 3*[ table]

    doc = SimpleDocTemplate( filename=context, pagesize=pagesize)
    if not OUT2PDF:
        doc.setPageCallBack( getattr( context, 'new_page', None))
    doc.build( story, canvasmaker=Canvas)


BUFFERED = 10
class MyCanvas(wx.ScrolledWindow):
    def __init__(me, parent, id = -1, size = wx.DefaultSize, *a, **ka):
        wx.ScrolledWindow.__init__(me, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)
        from measure import point2pix
        me.maxWidth, me.maxHeight = map( point2pix, (595.3, 841.9))

        me.SetBackgroundColour('WHITE')
        me.SetVirtualSize((me.maxWidth, me.maxHeight))
        me.SetScrollRate(40,40)

        if BUFFERED:
            me.buffer = wx.EmptyBitmap(me.maxWidth, me.maxHeight)
            dc = wx.BufferedDC(None, me.buffer)
            dc.SetBackground(wx.Brush(me.GetBackgroundColour()))
            dc.Clear()
            me.DoDrawing(dc)

        me.Bind(wx.EVT_PAINT, me.OnPaint)

    def OnPaint(me, event):
        if BUFFERED:
            dc = wx.BufferedPaintDC(me, me.buffer, wx.BUFFER_VIRTUAL_AREA)
        else:
            dc = wx.PaintDC(me)
            me.PrepareDC(dc)
            me.DoDrawing(dc)

    def DoDrawing(me, dc):
        from page_recorder import PageRecorder
        pagesize = (8.27 * inch, 11.69 * inch)
        rec = PageRecorder( pagesize)
        draw_table( rec, pagesize)

        dc.BeginDrawing()
        rec.draw_page( 0, dc)
        dc.EndDrawing()

        me.page_rec = rec

class TestPrintPanel(wx.Panel):
    Canvas = MyCanvas
    def __init__(me, frame, *a, **ka):
        wx.Panel.__init__(me, frame, -1)
        me.frame = frame

        me.printData = wx.PrintData()
        me.printData.SetPaperId(wx.PAPER_LETTER)
        me.printData.SetPrintMode(wx.PRINT_MODE_PRINTER)

        me.box = wx.BoxSizer(wx.VERTICAL)
        me.canvas = me.Canvas(me, *a, **ka)
        me.box.Add(me.canvas, 1, wx.GROW)

        subbox = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(me, -1, 'Page Setup')
        me.Bind(wx.EVT_BUTTON, me.OnPageSetup, btn)
        subbox.Add(btn, 1, wx.GROW | wx.ALL, 2)

        btn = wx.Button(me, -1, 'Print Preview')
        me.Bind(wx.EVT_BUTTON, me.OnPrintPreview, btn)
        subbox.Add(btn, 1, wx.GROW | wx.ALL, 2)

        btn = wx.Button(me, -1, 'Print')
        me.Bind(wx.EVT_BUTTON, me.OnDoPrint, btn)
        subbox.Add(btn, 1, wx.GROW | wx.ALL, 2)

        me.box.Add(subbox, 0, wx.GROW)

        me.SetAutoLayout(True)
        me.SetSizer(me.box)


    def OnPageSetup(me, evt):
        psdd = wx.PageSetupDialogData(me.printData)
        psdd.CalculatePaperSizeFromId()
        dlg = wx.PageSetupDialog(me, psdd)
        dlg.ShowModal()

        # this makes a copy of the wx.PrintData instead of just saving
        # a reference to the one inside the PrintDialogData that will
        # be destroyed when the dialog is destroyed
        me.printData = wx.PrintData( dlg.GetPageSetupData().GetPrintData() )

        dlg.Destroy()

    def OnPrintPreview(me, event):
        data = wx.PrintDialogData(me.printData)
        printout = MyPrintout(me.canvas.page_rec)
        printout2 = MyPrintout(me.canvas.page_rec)
        me.preview = wx.PrintPreview(printout, printout2, data)

        if not me.preview.Ok():
            print 'Houston, we have a problem...\n'
            return

        pfrm = wx.PreviewFrame(me.preview, me.frame, 'This is a print preview')

        pfrm.Initialize()
        pfrm.SetPosition(me.frame.GetPosition())
        pfrm.SetSize(me.frame.GetSize())
        pfrm.Show(True)


    def OnDoPrint(me, event):
        pdd = wx.PrintDialogData(me.printData)
        pdd.SetToPage(1)
        printer = wx.Printer(pdd)
        printout = MyPrintout(me.canvas.page_rec)

        if not printer.Print(me.frame, printout, True):
            wx.MessageBox('There was a problem printing.\nPerhaps your current printer is not set correctly?',
                          'Printing', wx.OK)
        else:
            me.printData = wx.PrintData( printer.GetPrintDialogData().GetPrintData() )
        printout.Destroy()


def test_exec( drawing_func):
    from page_recorder import PageRecorder
    printData = wx.PrintData()
    printData.SetPaperId( wx.PAPER_A4)
    printData.SetPrintMode( wx.PRINT_MODE_PRINTER)

    data = wx.PrintDialogData( printData)

    pagesize = (8.27 * inch, 11.69 * inch)
    page_rec = PageRecorder( pagesize)
    drawing_func( page_rec, pagesize)

    printout = MyPrintout( page_rec)
    printout2 = MyPrintout( page_rec)
    preview = wx.PrintPreview( printout, printout2, data)
    if not preview.Ok():
        print 'Houston, we have a problem...\n'
        raise SystemExit
    preview.SetZoom( 100)

    pfrm = wx.PreviewFrame( preview, None, 'This is a print preview')
    pfrm.Initialize()
    #pfrm.SetPosition( frame.GetPosition())
    pfrm.SetSize( map( int, (8.27*72+0.5, 11.69*72+0.5)))
    pfrm.Show(True)


if __name__ == '__main__':
    app = wx.PySimpleApp()
    if 0:
        frame = wx.Frame(None, -1, 'Dummy frame')
        frame.SetSize( map( int, (8.27*72+0.5, 11.69*72+0.5)))  #*72 щото rl-coords са в points=inch/72
        win = TestPrintPanel( frame)
        frame.Show()
    else:
        test_exec( draw_table)
    app.MainLoop()

# vim:ts=4:sw=4:expandtab
