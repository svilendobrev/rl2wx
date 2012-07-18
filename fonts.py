#$Id: fonts.py 7370 2009-02-02 16:19:08Z hristo $

# where to search for fonts
FontFolders = [
    '%(windir)s/Fonts',                         # windows xp has it set to where it is installed
    '/usr/share/fonts/truetype/msttcorefonts',  # from msttcorefonts ubuntu package
    '/usr/share/fonts/X11/Type1',               # X fonts
    '%(home)s/tmp/corefonts',                   # extra
]

from reportlab.lib.fontfinder import FontFinder
from reportlab.lib import fonts
from reportlab import rl_config
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import os
env = {
    'windir': os.environ.get('windir',os.getcwd()),
    'home'  : os.environ.get('HOME',os.getcwd()),
}

folders = [ s % env for s in FontFolders ]
ff = FontFinder( useCache=False)
paths = ( rl_config.TTFSearchPath, rl_config.T1SearchPath, rl_config.CMapSearchPath)
for p in paths:
    if isinstance( p, list):
        folders += p
    else:
        folders.append( p)

ff.addDirectories( set( folders) )
ff.search()


_registered_font_names = {}

def register_font( font_name, family=''):
    try: return _registered_font_names[ font_name]
    except KeyError: pass

    found = ff.getFontsWithAttributes( name=font_name)
    if not found:
        #print '%(font_name)s not found, loading default for rl_config %(res)s' % locals()
        res = rl_config.defaultGraphicsFontName
    else:
        descr = found[0]
        if descr.typeCode == 'ttf':
            font = TTFont( descr.name, descr.fileName)
        else:
            face = pdfmetrics.EmbeddedType1Face( descr.metricsFileName, descr.fileName)
            pdfmetrics.registerTypeFace( face)
            font = pdfmetrics.Font( font_name, font_name, rl_config.defaultEncoding)
        pdfmetrics.registerFont( font)
        res = font_name
    if 10:
        from reportlab.lib.fonts import addMapping
        bold = int('Bold' in font_name)
        italic = int('Italic' in font_name)
        addMapping( family or font_name, bold, italic, font_name)
    _registered_font_names[ font_name ] = res
    return res


if 0 or __name__ == '__main__':
    print '\n'.join( folders)
    for familyName in ff.getFamilyNames():
        print '%s' % familyName

        for font in ff.getFontsInFamily( familyName):
            print '\t\t%s' % font.name, font.fileName
            register_font( font.name, familyName)

# vim:ts=4:sw=4:expandtab
