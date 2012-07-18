
import  wx

BUFFERED = 1

#---------------------------------------------------------------------------

class MyCanvas(wx.Window):
    def __init__(self, parent, id = -1, size = (500,400)):
        wx.Window.__init__(self, parent, id, (0, 0), size=size, style=wx.SUNKEN_BORDER)

        self.lines = []
        self.x = self.y = 0
        self.curLine = []
        self.drawing = False

        self.SetBackgroundColour("GRAY")
        self.SetCursor(wx.StockCursor(wx.CURSOR_PENCIL))

        if BUFFERED:
            # Initialize the buffer bitmap.  No real DC is needed at this point.
            self.buffer = wx.EmptyBitmap( size[0], size[1])
            dc = wx.BufferedDC(None, self.buffer)
            dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
            dc.Clear()
            self.DoDrawing(dc)

        self.Bind(wx.EVT_PAINT, self.OnPaint)


    def getWidth(self):
        return self.maxWidth

    def getHeight(self):
        return self.maxHeight


    def OnPaint(self, event):
        if BUFFERED:
            # Create a buffered paint DC.  It will create the real
            # wx.PaintDC and then blit the bitmap to it when dc is
            # deleted.  Since we don't need to draw anything else
            # here that's all there is to it.
            dc = wx.BufferedPaintDC(self, self.buffer)#, wx.BUFFER_VIRTUAL_AREA)
        else:
            dc = wx.PaintDC(self)
            self.PrepareDC(dc)
            # since we're not buffering in this case, we have to
            # paint the whole window, potentially very time consuming.
            self.DoDrawing(dc)


    def DoDrawing(self, dc, printing=False):
        print dc.GetDeviceOrigin()
        dc.SetMapMode( wx.MM_TEXT)
        dc.SetAxisOrientation( True, True)
        dc.SetDeviceOrigin( 0, dc.GetSize().y-1)
        dc.BeginDrawing()

        if 1:
            mm = 1
            dc.SetMapMode( wx.MM_METRIC)
        else:
            m = dc.GetPPI()
            mm = 72 / 2.54 / 10
        print dc.GetSize(), dc.GetSizeMM(), dc.GetDeviceOrigin()
        print dc.GetPPI(), wx._misc.GetDisplaySize(), wx._misc.GetDisplaySizeMM()

        x2 = 30*mm

        for i in range( 8, 20*4,2):
            dc.SetPen( wx.Pen( i % 8 and 'GREEN' or 'RED', 0.2))
            y = i*mm
            dc.DrawLine( 0, y, x2, y)
        y=20*4
        dc.DrawLine( 0, y, x2+5, y)
        dc.SetPen( wx.Pen( 'BLACK', 0.2))
        dc.DrawLine( 0, 0, 130, 0)

        font = wx.Font( 20, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, "Bitstream Charter")
        szmm = 190 * (25.4/72)
        sz = szmm * 72.0/dc.GetPPI().y
        font.SetPointSize( sz)
        dc.SetFont( font)
        ww,hh,dec,lead = dc.GetFullTextExtent('p')
        dc.SetTextForeground( wx.BLACK)
        dc.DrawText("Ap12345", 0, 0+ hh-dec)

        dc.EndDrawing()


    def DrawSavedLines(self, dc):
        dc.SetPen(wx.Pen('MEDIUM FOREST GREEN', 4))

        for line in self.lines:
            for coords in line:
                apply(dc.DrawLine, coords)


    def SetXY(self, event):
        self.x, self.y = self.ConvertEventCoords(event)

    def ConvertEventCoords(self, event):
        newpos = self.CalcUnscrolledPosition(event.GetX(), event.GetY())
        return newpos

## This is an example of what to do for the EVT_MOUSEWHEEL event,
## but since wx.ScrolledWindow does this already it's not
## necessary to do it ourselves. You would need to add an event table
## entry to __init__() to direct wheelmouse events to this handler.

##     wheelScroll = 0
##     def OnWheel(self, evt):
##         delta = evt.GetWheelDelta()
##         rot = evt.GetWheelRotation()
##         linesPer = evt.GetLinesPerAction()
##         print delta, rot, linesPer
##         ws = self.wheelScroll
##         ws = ws + rot
##         lines = ws / delta
##         ws = ws - lines * delta
##         self.wheelScroll = ws
##         if lines != 0:
##             lines = lines * linesPer
##             vsx, vsy = self.GetViewStart()
##             scrollTo = vsy - lines
##             self.Scroll(-1, scrollTo)

#---------------------------------------------------------------------------

def runTest(frame, nb, log):
    win = MyCanvas(nb)
    return win

#---------------------------------------------------------------------------



overview = """
<html>
<body>
The wx.ScrolledWindow class manages scrolling for its client area, transforming the
coordinates according to the scrollbar positions, and setting the scroll positions,
thumb sizes and ranges according to the area in view.
</body>
</html>
"""


if __name__ == '__main__':
    import sys,os
    import run
    run.main(['', os.path.basename(sys.argv[0])] + sys.argv[1:])


