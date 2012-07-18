#$Id: textobject.py 8436 2009-04-27 09:46:29Z hristo $
# -*- coding: cp1251 -*-

from reportlab.pdfgen.textobject import PDFTextObject
from reportlab.lib.colors import toColor
from reportlab.pdfbase import pdfmetrics
from recorder import Recorder

class TextObject( PDFTextObject):
    def __init__(me, canvas, x=0,y=0):
        me.recorder = Recorder()
        PDFTextObject.__init__( me, canvas, x, y)

    def getCode(me):
        return 'dummy'

    def setFillColorRGB(me, r, g, b):
        """Set the fill color using positive color description
           (Red,Green,Blue).  Takes 3 arguments between 0.0 and 1.0"""
        return me.setFillColor( (r, g, b))

    def setFillColor(me, aColor):
        """Takes a color object, allowing colors to be referred to by name"""
        color = toColor( aColor)
        if color:
            me.recorder.SetTextForeground( *color.bitmap_rgb())
        else:
            raise 'Unknown color', str(aColor)

    def setTextOrigin(me, x, y):
        #self._code.append('1 0 0 1 %s Tm' % fp_str(x, y)) #bottom up
        # wx can't draw inverted text so bottomup is ignored here
        #me.recorder.Transform( 1, 0, 0, 1, x, y)
        # The current cursor position is at the text origin
        me._x0 = me._x = x
        me._y0 = me._y = y

    def setTextTransform(me, a, b, c, d, e, f):
        "Like setTextOrigin, but does rotation, scaling etc."
        #me.recorder.Transform( a, b, c, d, e, f)

        # The current cursor position is at the text origin Note that
        # we aren't keeping track of all the transform on these
        # coordinates: they are relative to the rotations/sheers
        # defined in the matrix.
        me._x0 = me._x = e
        me._y0 = me._y = f

    def moveCursor(me, dx, dy):
        """Starts a new line at an offset dx,dy from the start of the
        current line. This does not move the cursor relative to the
        current position, and it changes the current offset of every
        future line drawn (i.e. if you next do a textLine() call, it
        will move the cursor to a position one line lower than the
        position specificied in this call.  """

        #self._code.append('%s Td' % fp_str(dx, -dy))
        me.recorder.Translate( dx, -dy)

        # Keep track of the new line offsets and the cursor position
        me._x0 += dx
        me._y0 += dy
        me._x = me._x0
        me._y = me._y0

    def setFont(me, psfontname, size, leading = None):
        """Sets the font.  If leading not specified, defaults to 1.2 x
        font size. Raises a readable exception if an illegal font
        is supplied.  Font names are case-sensitive! Keeps track
        of font anme and size for metrics."""
        me._fontname = psfontname
        me._fontsize = size
        if leading is None:
            leading = size * 1.2
        me._leading = leading
        me.recorder.SetFont( me._fontname, me._fontsize)

    def _textOut(me, text, TStar=0):
        "prints string at current point, ignores text cursor"
        if not TStar:
            me.recorder.DrawText( text, me._x, me._y)
        else:
            me.textLine( text)

    def textOut(me, text):
        """prints string at current point, text cursor moves across."""
        me._textOut( text)
        if 1:
            me._x = me._x + me._canvas.stringWidth(text, me._fontname, me._fontsize)
        else:
            w,h = me.recorder.GetTextExtent( text)
            print 'wx says:', w, 'reportlab says:', me._canvas.stringWidth(text, me._fontname, me._fontsize)
            me._x = me._x + w

    def textLine(me, text=''):
        """prints string at current point, text cursor moves down.
        Can work with no argument to simply move the cursor down."""

        me.recorder.DrawText( text, me._x, me._y)
        # Update the coordinates of the cursor
        me._x = me._x0
        me._y -= me._leading

        # Update the location of the start of the line
        # me._x0 is unchanged
        me._y0 = me._y

    def __nonzero__(me):
        'PDFTextObject is true if it has something done after the init'
        return me.recorder.method_calls #me._code != ['BT']


# vim:ts=4:sw=4:expandtab
