#$Id: canvas.py 8436 2009-04-27 09:46:29Z hristo $
# -*- coding: cp1251 -*-

from reportlab.pdfgen.canvas import Canvas as ReportlabCanvas
from reportlab.lib.colors import toColor
from reportlab import rl_config
from recorder import Recorder

class Form( object):
    def __init__( me, lowerx=0, lowery=0, upperx=None, uppery=None):
        me.lowerx = lowerx
        me.lowery = lowery
        me.upperx = upperx
        me.uppery = uppery
        me.recorder = Recorder()


class Canvas( ReportlabCanvas):
    ''' A substitute for the reportlab canvas to draw on an arbitrary device context.
        No wx stuff is used here, so as much as the context conforms to the required interface
        it can be anything.
    '''
    @property
    def context( me):
        return me._recorders[ -1]

    def __init__( me,
                filename, # here pass a context object
                pagesize=None,
                bottomup = 1,
                pageCompression=None,
                invariant = None,
                verbosity=0):

        me._recorders = [ filename]
        me._forms = {} # name : recorder

        #just to fool platypus we are reportlab's native canvas
        from reportlab.pdfbase import pdfdoc
        me._doc = pdfdoc.PDFDocument(compression=pageCompression, invariant=invariant)

        if pagesize is None:
            pagesize = rl_config.defaultPageSize

        #print '---------canvas pagesize', pagesize
        #print '---------in inches', [ sz / 72.0 for sz in pagesize ]

        me._pagesize = pagesize
        me._pageNumber = 1   # keep a count
        me._onPage = None

        me.bottomup = bottomup  # for not printing inverted texts
        me.init_graphics_state()
        me._state_stack = []

    def save(me):
        pass

    def showPage(me):
        if me._onPage:
            #me._onPage(me._pageNumber)
            me._onPage( *me._pagesize)

        me._pageNumber += 1
        me.init_graphics_state()
        me._state_stack = []

    # graphics state
    STATE_ATTRIBUTES = dict(
        #_currentMatrix  = (1., 0., 0., 1., 0., 0.), # not used
        # font
        _fontname       = 'Times-Roman',
        _fontsize       = 14,
        _leading        = 14.4,
        _wordSpace      = 0,
        # pen
        _lineCap        = 0,
        _lineJoin       = 0,
        _lineDash       = None,#[1,2],
        _lineWidth      = 0,
        _mitreLimit     = 0,
        _strokeColorRGB = 3*[ 0],
        # brush
        _fillMode       = 0,  #0=even_odd; 1=winding_rule
        _fillStyle      = 1,  #0=transparent 1=solid
        _fillColorRGB   = 3*[ 255],
    )
    # not used
    #_x _y _textMode _charSpace _horizScale _textRenderMode _rise _textLineMatrix _textMatrix

    def init_graphics_state( me):
        for attr_name, default in me.STATE_ATTRIBUTES.iteritems():
            setattr( me, attr_name, default)

        me._set_brush()
        me._set_pen()
        me._set_font()

    def saveState(me):
        me.context.PushState()

        state = {}
        d = me.__dict__
        for name in me.STATE_ATTRIBUTES.iterkeys():
            state[name] = d[name]
        me._state_stack.append(state)

    def restoreState(me):
        me.context.PopState()

        state = me._state_stack.pop()
        d = me.__dict__
        d.update(state)

    # basic graphics settings
    def setFont(me, psfontname, size, leading = None):
        me._fontname = psfontname
        me._fontsize = size
        if leading is None:
            leading = size * 1.2
        me._leading = leading
        me._set_font()

    def setFontSize(me, size=None, leading=None):
        if size is None: size = me._fontsize
        if leading is None: leading = me._leading
        me.setFont(me._fontname, size, leading)

    def setLineWidth(me, width):
        me._lineWidth = width
        me._set_pen()

    def setLineCap(me, mode):
        assert mode in [0,1,2], 'Line caps allowed: 0=butt,1=round,2=square'
        me._lineCap = mode
        me._set_pen()

    def setLineJoin(me, mode):
        assert mode in [0,1,2], 'Line Joins allowed: 0=mitre, 1=round, 2=bevel'
        me._lineJoin = mode
        me._set_pen()

    def setDash(me, array=[], phase=0):
        '''Two notations.  pass two numbers, or an array and phase'''
        arg = []
        if isinstance( array, (list, tuple)):
            arg = array + [phase]
        else:
            arg = [ array, phase]
        me._lineDash = arg
        me._set_pen()

    def setFillColor(me, aColor):
        '''Takes a color object, allowing colors to be referred to by name'''

        color = toColor( aColor)
        if color:
            me._fillColorRGB = color.bitmap_rgb()
            me._set_brush()
        else:
            raise 'Unknown color', str(aColor)

    def setFillColorRGB( me, r, g, b):
        '''Set the fill color using positive color description
           (Red,Green,Blue).  Takes 3 arguments between 0.0 and 1.0'''
        return me.setFillColor( (r, g, b))

    def setStrokeColor(me, aColor):
        color = toColor( aColor)
        if color:
            me._strokeColorRGB = color.bitmap_rgb()
            me._set_pen()
        else:
            raise 'Unknown color', str(aColor)

    def setStrokeColorRGB( me, r, g, b):
        '''Set the stroke color using positive color description
           (Red,Green,Blue).  Takes 3 arguments between 0.0 and 1.0'''
        return me.setStrokeColor( (r,g,b))

    def _set_pen( me, style =1): # style: 0-transparent, 1-solid
        me.context.SetPen( me._strokeColorRGB, me._lineWidth, me._lineDash, me._lineCap, me._lineJoin, style=style)

    def _set_brush( me):
        me.context.SetBrush( me._fillColorRGB, me._fillStyle, me._fillMode)

    def _set_font( me):
        from reportlab.pdfbase.pdfmetrics import getFont

        from fonts import ff
        fonts = ff.getFontsWithAttributes( name=me._fontname)
        params = [ me._fontname, me._fontsize ]
        if fonts:
            #print 'FOUND IT', fonts
            f = fonts[0]
            params += [ f.isBold, f.isItalic ]
        else:
            from reportlab.pdfbase.pdfmetrics import getTypeFace
            try:
                f = getTypeFace( me._fontname)
            except KeyError: pass
            else:
                params += [ f.bold, f.italic ]
        me.context.SetFont( *params)

    # path stuff - a separate path object builds it
    def beginPath(me):
        ''' The object returned must follow the protocol for a pathobject.PDFPathObject instance'''
        from pathobject import PathObject
        return PathObject()

    def drawPath(me, aPath, stroke=1, fill=0):
        me.context.DrawPath( aPath, stroke, fill, me._fillMode)

    def clipPath(me, aPath, stroke=1, fill=0):
        'clip as well as drawing'
        me.context.ClipPath( aPath, stroke, fill)

    # shapes drawing
    def line(me, x1,y1, x2,y2):
        me.context.DrawLine( x1, y1, x2, y2)

    def lines(me, linelist):
        for (x1,y1,x2,y2) in linelist:
            me.line( x1, y1, x2, y2)

    def rect(me, x, y, width, height, stroke=1, fill=0):
        if 0:
            path = me.beginPath()
            path.rect( x, y, width, height)
            me.drawPath( path, stroke, fill)
        else:
            me.context.PushState()
            me._set_pen( 0)
            me.context.DrawRectangle( x, y, width, height)
            me.context.PopState()

    def bezier(me, x1, y1, x2, y2, x3, y3, x4, y4):
        'Bezier curve with the four given control points'
        pass #TODO

    def arc(me, x1,y1, x2,y2, startAng=0, extent=90):
        path = me.beginPath()
        path.arc( x1, y1, x2, y2, startAng, extent)
        me.drawPath( path)

    def wedge(me, x1,y1, x2,y2, startAng, extent, stroke=1, fill=0):
        '''Like arc, but connects to the centre of the ellipse.
        Most useful for pie charts and PacMan!'''
        pass #TODO

    def ellipse(me, x1, y1, x2, y2, stroke=1, fill=0):
        path = me.beginPath()
        width = abs( x1-x2)
        height = abs( y1-y2)
        path.ellipse( x1, y1, width, height)
        me.drawPath( path, stroke, fill)


    # trasformations
    def transform(me, a,b,c,d,e,f):
        me.context.Transform( a,b,c,d,e,f)

    # text
    def drawString( me, x, y, text):
        me.context.DrawText( text, x, y)
        #me.line( x, y, x+20, y+10)

    def drawRightString(me, x, y, text):
        '''Draws a string right-aligned with the x coordinate'''
        width = me.stringWidth(text, me._fontname, me._fontsize)
        me.drawString( x - width, y, text)

    def drawCentredString(me, x, y, text):
        '''Draws a string centred on the x coordinate.'''
        width = me.stringWidth(text, me._fontname, me._fontsize)
        me.drawString( x - 0.5*width, y, text)

    def beginText(me, x=0, y=0):
        from textobject import TextObject
        return TextObject( me, x, y)

    def drawText(me, aTextObject):
        me.context.DrawTextObject( aTextObject)

    def beginForm(me, name, lowerx=0, lowery=0, upperx=None, uppery=None):
        '''declare the current graphics stream to be a named form.
           A graphics stream can either be a page or a form, not both.
           Some operations (like bookmarking) are permitted for pages
           but not forms.  The form will not automatically be shown in the
           document but must be explicitly referenced using doForm in pages
           that require the form.'''
        me.saveState()
        me.init_graphics_state()
        (w,h) = me._pagesize
        form = Form( lowerx, lowery, upperx or w, uppery or h)
        me._forms[ name] = form # replace existing ??
        me._recorders.append( form.recorder)

    def endForm(me):
        '''emit the current collection of graphics operations as a Form
           as declared previously in beginForm.'''
        me._recorders.pop()
        me.restoreState()

    def doForm(me, name):
        if not me.hasForm( name): return

        form = me._forms[ name]
        form.recorder.play_on( me.context)

    def hasForm(me, name):
        return name in me._forms



    #######################################
    # TODO

    def drawInlineImage(self, *args, **kargs):
        img_width = img_height = 0
        return (img_width, img_height)

    def drawImage(self, *args, **kargs):
        img_width = img_height = 0
        return (img_width, img_height)

    def setPageCompression(me, pageCompression=1):
        '''Possible values None, 1 or 0
        If None the value from rl_config will be used.
        If on, the page data will be compressed, leading to much
        smaller files, but takes a little longer to create the files.
        This applies to all subsequent pages, or until setPageCompression()
        is next called.'''
        pass

    def setPageRotation(me, rot):
        '''Instruct display device that this page is to be rotated'''
        assert rot % 90.0 == 0.0, 'Rotation must be a multiple of 90 degrees'
        pass


        # pdf specific stuff - only for the sake of interface
    def bookmarkPage(me, key,
                      fit="Fit",
                      left=None,
                      top=None,
                      bottom=None,
                      right=None,
                      zoom=None
                      ):
        pass

    def linkAbsolute(me, contents, destinationname, Rect=None, addtopage=1, name=None,
            thickness=0, color=None, dashArray=None, **kw):
        pass

    def linkRect(me, contents, destinationname, Rect=None, addtopage=1, name=None, relative=1,
            thickness=0, color=None, dashArray=None, **kw):
        pass

    def linkURL(me, url, rect, relative=0, thickness=0, color=None, dashArray=None, kind="URI", **kw):
        pass

    def showOutline( me):
        '''Specify that Acrobat Reader should start with the outline tree visible.
        showFullScreen() and showOutline() conflict; the one called last
        wins.'''
        pass

    def addLiteral(me, s, escaped=1):
        '''introduce the literal text of PDF operations s into the current stream.
           Only use this if you are an expert in the PDF file format.'''
        pass

    def getpdfdata(me):
        '''Returns the PDF data that would normally be written to a file.
        If there is current data a ShowPage is executed automatically.
        After this operation the canvas must not be used further.'''
        pass


if __name__ == '__main__':
    from reportlab.test.test_pdfgen_pycanvas import makeDocument
    from test import test_exec
    import sys

    debug = 0
    if len(sys.argv) > 1:
        debug = int(sys.argv[1])


    from canvas import Canvas as ActualCanvas
    class ActualCanvas( Canvas):
        def __init__( me,
                    filename, # here pass a context object
                    pagesize=None,
                    bottomup = 1,
                    pageCompression=None,
                    invariant = None,
                    verbosity=0):
            Canvas.__init__( me, filename, pagesize, bottomup, pageCompression, invariant, verbosity)
            from measure import point2pix
            sz = map( point2pix, (595.3, 841.9))
            me.setPageSize( sz)

        def showPage(me):
            Canvas.showPage( me)
            me.context.new_page( *me._pagesize)

    def do_test( page_rec, (width, height)):
        Canvas = ActualCanvas
        from reportlab.pdfgen import pycanvas
        from reportlab.lib.colors import Color

        pycanvas.PyHeader = ''
        pycanvas.PyFooter = ''

        #import canvas as pycanvas # makeDocument must see us as pycanvas
        pycanvas = makeDocument( 'canvas_test_sample.pdf')
        pycanvas.save()

        code = '\n'.join( line.strip() for line in pycanvas._pyfile.getvalue().split('\n')) #clear indent
        file = page_rec
        page_rec.DEBUG = debug
        exec ( code, locals())
        page_rec.new_page( width, height)

    import wx
    app = wx.PySimpleApp()
    test_exec( do_test)
    app.MainLoop()



# vim:ts=4:sw=4:expandtab
