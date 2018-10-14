import wx


def IMG_RESIZE(path, max_width, max_height):
    '''Function for resizing images'''
    image = wx.Image(path)
    width, height = image.GetWidth(), image.GetHeight()

    if width > max_width:
        width, height = (max_width, height * (max_width / float(width)))
    if height > max_height:
        width, height = (width * (max_height / float(height)), max_height)
    image.Rescale(width, height, wx.IMAGE_QUALITY_HIGH)
    
    return image
