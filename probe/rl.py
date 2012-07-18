def coords(canvas):
    from reportlab.lib.units import inch, mm
    from reportlab.lib.colors import pink, black, red, blue, green
    from reportlab.pdfbase import pdfmetrics

    c = canvas
    #c.grid([inch, 2*inch, 3*inch, 4*inch], [0.5*inch, inch, 1.5*inch, 2*inch, 2.5*inch])

    x1 = 10*mm
    x2 = x1 + 30*mm

    c.setLineWidth( 0.1)

    for i in range( 8, 20*4,2):
        c.setStrokeColor( i % 8 and green or red)
        y = i * mm
        c.line( x1, y, x2, y)
    y=20*4*mm
    c.setStrokeColor( green)
    c.line( 0, y, x2+5, y)
    c.setStrokeColor( black)
    c.line( 0, 0, 130, 0)

    from reportlab import rl_config
    rl_config.T1SearchPath.insert( 0, '/usr/share/fonts/X11/Type1/')
    pdfmetrics.dumpFontData()
    fontname = 'CharterBT-Roman'
    pdfmetrics.findFontAndRegister( fontname)
    fontsize = 190
    c.setFont( fontname, fontsize)

    c.drawString( 0*mm, 0, 'Ap12345')

    if 0:
        point = inch / 72.0

        text = 'Aa'
        width = canvas.stringWidth( 'A', font, fontsize)

        y1 = 10*mm
        from math import sqrt
        height = sqrt(fontsize**2 - width**2)
        y2 = y1 + height

        c.setStrokeColor( red)
        coords = [ mm * i for i in range(10,10+int(height)) ]
        c.grid( coords, coords)

        c.setStrokeColor( green)
        c.line( 10*mm, y1, 300*mm, y1)
        c.line( 10*mm, y2, 300*mm, y2)
        c.setFont( font, fontsize)

        c.setStrokeColor( black)
        c.drawString( 10*mm, y1, text)

from reportlab.pdfgen.canvas import Canvas

canvas = Canvas('outppp.pdf')
coords( canvas)
canvas.save()
