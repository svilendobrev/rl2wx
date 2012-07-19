#$Id: printout.py 8436 2009-04-27 09:46:29Z hristo $


import wx

class MyPrintout(wx.Printout):
    def __init__(me, page_rec):
        wx.Printout.__init__(me)
        me.page_rec = page_rec
        me.page_rec.DEBUG = 0

    def HasPage(me, page):
        if page <= len(me.page_rec.pages):
            return True
        else:
            return False

    def GetPageInfo(me):
        return 2 * (1, len(me.page_rec.pages))

    def OnPrintPage(me, page):
        page_num0based = page - 1
        dc = me.GetDC()

        dc.SetUserScale( 1.0, 1.0)
        dc.SetMapMode( wx.MM_TEXT)
        dc_width_pixels, dc_height_pixels = dc.GetSizeTuple()

        #XXX let wx convert pixels to points
        dc_width_device  = dc.LogicalToDeviceXRel( dc_width_pixels)
        dc_height_device = dc.LogicalToDeviceYRel( dc_height_pixels)
        dc.SetMapMode( wx.MM_POINTS)
        dc_size_points = [
            dc.DeviceToLogicalXRel( dc_width_device),
            dc.DeviceToLogicalYRel( dc_height_device),
        ]

        if 1:
            page_size_points = me.page_rec.get_pagesize( page_num0based)
        else:
            table = me.page_rec.debug_table
            doc   = me.page_rec.debug_doc
            page_size_points = [table._width, table._height]
            page_size_points = (doc.width, doc.height)
            frames = doc.pageTemplate.frames
            print frames
            page_size_points = ( frames[ page_num0based].width, frames[page_num0based].height)

        if page_size_points:
            actualScale = min( [ float( sz[0]) / sz[1]
                                 for sz in zip( dc_size_points, page_size_points) ] )
            if 0:
                print 'dc points=', dc_size_points, 'pixels=', dc_width_pixels, dc_height_pixels
                print 'page points=', page_size_points
                print 'scale=', actualScale

            dc.SetUserScale( actualScale, actualScale)
            me.page_rec.draw_page( page_num0based, dc)
        else:
            print 'page %s not found' % str(page_num0based)
        return True


# vim:ts=4:sw=4:expandtab
