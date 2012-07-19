#$Id: measure.py 8436 2009-04-27 09:46:29Z hristo $


import wx

def points_per_inch( dc):
    old_map_mode = dc.GetMapMode()
    old_user_scale = dc.GetUserScale()

    dc.SetUserScale( 1.0, 1.0)
    dc.SetMapMode( wx.MM_TEXT)
    pixels_per_inch = dc.GetPPI() # always pixels, regardless of current mapping mode
    device_units_per_inch = (
                        dc.LogicalToDeviceXRel( pixels_per_inch[0]),
                        dc.LogicalToDeviceYRel( pixels_per_inch[1])
                      )

    dc.SetMapMode( wx.MM_POINTS)
    points_per_inch = (
                        dc.DeviceToLogicalXRel( device_units_per_inch[0]),
                        dc.DeviceToLogicalYRel( device_units_per_inch[1])
                      )
    dc.SetMapMode( old_map_mode)
    dc.SetUserScale( *old_user_scale)
    return points_per_inch

def dc_coef_pix2points( dc):
    pixels = dc.GetPPI()
    points = points_per_inch( dc)
    return [ float(pt) / pix for (pt,pix) in zip(points, pixels) ]

def dc_coef_scale_to_dpi72( dc):
    pdf_points = 72.0
    dc_points = points_per_inch( dc)
    return [ pdf_points / sz for sz in dc_points ]

def pixpermm():
    return float(wx._misc.GetDisplaySize()[1]) / wx._misc.GetDisplaySizeMM()[1]

def pixperinch():
    return pixpermm() * 25.4

def mm2pix(x):
    return pixpermm() * x

def inch2pix(x):
    return pixperinch() * x

def point2pix(x):
    return pixpermm() * 25.4/72 * x

def pix2points(x):
    return (x / pixperinch()) * 72

def mm2points(x):
    return pix2points( mm2pix( x))



# vim:ts=4:sw=4:expandtab
