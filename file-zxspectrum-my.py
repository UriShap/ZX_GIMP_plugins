#!/usr/bin/env python
# coding:utf-8

# GIMP Plug-in for the ZX-Spectrum binary screen file format

# Copyright (C) 2017 by João S. O. Bueno <gwidion@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Plug-in structure based on the Open Raster plug-in by Jn Nordy, on GIMP source tree.
# ==============================================
# UriS: fixed some errors, 
# add save .scr,
# add color (255, 127, 0) as an invisible color
# ----------------------------------------------

from __future__ import print_function

from  gimpfu import *
from os import name as os_name
from sys import stderr as sys_stderr

SIZE = WIDTH, HEIGHT = 256, 192

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
# orange for invisible pixels
INVISIBLE = (255, 127, 0) 

COLORS = [  (0, 0, 0), (0, 0, 192), (192, 0 ,0), (192, 0, 192),
            (0, 192, 0), (0, 192, 192), (192, 192, 0), (192, 192, 192),
            (0, 0, 0), (0, 0, 255), (255, 0, 0), (255, 0, 255),
            (0, 255, 0), (0, 255, 255), (255, 255, 0), (255, 255, 255), 
	    (255, 127, 0), ]

ATTR_I = (0x00, 0x01, 0x02, 0x03,
          0x04, 0x05, 0x06, 0x07,
          0x00, 0x41, 0x42, 0x43,
          0x44, 0x45, 0x46, 0x47,
          0x80, )

ATTR_P = (0x00, 0x08, 0x10, 0x18, 
          0x20, 0x28, 0x30, 0x38, 
          0x00, 0x48, 0x50, 0x58, 
          0x60, 0x68, 0x70, 0x78, 
          0x80, )

C2I = dict(zip(COLORS, ATTR_I))
C2P = dict(zip(COLORS, ATTR_P))

def save_speccy(img, drawable, filename, raw_filename):
    h = pdb.gimp_drawable_height(drawable)
    w = pdb.gimp_drawable_width(drawable)
    if w != 256 or h != 192:
        pdb.gimp_message("image size must be 256x192")
        return
    data = []
    for y in range (0,h):
        for x in range (0,w):
            c = pdb.gimp_drawable_get_pixel(drawable, x, y)[1]
	    c = (c[0], c[1], c[2])
            if c not in COLORS:
                pdb.gimp_message("invalid color %r at (%r, %r)" % (c,x,y,))
                return
            data.append(c)
# -------------------------------------------------------------------------------
    pixels = []
    attrib = []
    for y in range(0, h, 8):
        for x in range(0, w, 8):
            byte = []
            attr = []
            for j in range(8):
                row = 0
                for i in range(8):
                    if not attr:
                        attr.append(data[x + i + (j + y) * w])
                    if data[x + i + (j + y) * w] != attr[0]:
                        row |= 1 << (7 - i)
                    if data[x + i + (j + y) * w] not in attr:
                        attr.append(data[x + i + (j + y) * w])
                byte.append(row)

            if len(attr) > 2:
                pdb.gimp_message("more than 2 colors in an attribute block in (%d, %d)" % (x, y))
                return
            elif len(attr) != 2:
                # if only one colour, try to find a match in an adjacent cell
                if attr[0]==COLORS[16]:
                   attr.append(COLORS[0])
                if attrib:
                    prev_attr = attrib[-1]
                    if prev_attr[0] == attr[0]:
                        attr.append(prev_attr[1])
                if len(attr) != 2:
                    attr.append(COLORS[0])

            # improve compression ratio
#            if C2P[attr[0]] > C2I[attr[1]]: - fixed!
            if C2I[attr[0]] > C2I[attr[1]]:
                attr[0], attr[1] = attr[1], attr[0]
                byte = [~b & 0xff for b in byte]

            # add invisible pixels
            if attr[0]==COLORS[16]:
                attr[0]=attr[1]
            if attr[1]==COLORS[16]:
                attr[1]=attr[0]


            pixels.extend(byte)
            attrib.append(attr)

    attrib = [(C2P[attr[0]] | C2I[attr[1]]) for attr in attrib]

    interlaced = []
    for block in range(3):
        for col in range(8):
            for row in range(8):
                for line in range(32):
                    interlaced.append(pixels[block * 8 * 8 * 32
                                             + row * 32 * 8
                                             + line * 8
                                             + col])

    with open(filename, "wb") as fh:
        fh.write(bytearray(interlaced))
        fh.write(bytearray(attrib))

# ===============================================================================

#    print("Not implemented")
#    pass


def thumbnail_speccy(filename, thumbsize):
    return load_speccy(filename, filename)


def load_speccy(filename, raw_filename):
    path = raw_filename[len('file:///'):]\
        if os_name=='nt' else raw_filename[len('file://'):]
    # fixed spaces in file names for Windows
    path = path.replace('%20', ' ')
    data = open(path, "rb").read()
    if len(data) != 6912:
        pdb.gimp_message("Incorrect file size for {}: probably not a zx-spectrum scr.".format(filename),
              file=sys_stderr)

    img = gimp.Image(WIDTH, HEIGHT, RGB)
    layer = img.new_layer(mode=RGB)

    def setter(coords, color):
        v = coords + (4, color + (255,) )
        pdb.gimp_drawable_set_pixel(layer, *v)

    load_bitmap(setter, data)

    return img


def pygame_load(scr, data):
    """Loads the bitmap data of a speccy image given a pygame surface and file data."""
    return load_bitmap(scr.set_at, data)


def load_bitmap(pixel_setter, data):
    """Loads a speccy image as a bitmap given a 'set_pixel' function and file data"""
    offset = 0
    block = 0
    line = 0
    col = 0
    data = bytearray(data)
    attr_table = data[6144: 6912]
    while True:
        row_data = data[offset: offset + 32]
        tmp = (offset // 32)
        line = 8 * (tmp % 8) + (tmp // 8) % 8 + 64 * ((offset // 2048))
        if line >= 192: break
        for col, byte in enumerate(row_data):
            attribute = attr_table[ (line // 8 )*32 + col ]
            bright = 8 if attribute & 0x40 else 0
            ink = attribute & 0x07
            paper = (attribute & 0x38) // 8
            for pix in range(7, -1, -1):
		if ink==paper:
                   ink=16
                pixel_setter((col * 8 + pix  , line), COLORS[ ink | bright ]  if byte & 0x01 else COLORS[ paper | bright ] )
                byte >>= 1
        offset += 32


def register_load_handlers():
    gimp.register_load_handler('file-zxspectrum-load', 'scr', '')
    pdb['gimp-register-file-handler-mime']('file-zxspectrum-load', 'image/openraster')
    pdb['gimp-register-thumbnail-loader']('file-zxspectrum-load', 'file-zxspectrum-load-thumb')


def register_save_handlers():
    gimp.register_save_handler('file-zxspectrum-save', 'scr', '')


register(
    'file-zxspectrum-load-thumb', #name
    'loads a thumbnail from a ZX-Spectrum memory dump (.scr) file', #description
    'loads a thumbnail from a ZX-Spectrum memory dump (.scr) file',
    'João S. O. Bueno', #author
    'João S. O. Bueno', #copyright
    '2017', #year
    None,
    None, #image type
    [   #input args. Format (type, name, description, default [, extra])
        (PF_STRING, 'filename', 'The name of the file to load', None),
        (PF_INT, 'thumb-size', 'Preferred thumbnail size', None),
    ],
    [   #results. Format (type, name, description)
        (PF_IMAGE, 'image', 'Thumbnail image'),
        (PF_INT, 'image-width', 'Width of full-sized image'),
        (PF_INT, 'image-height', 'Height of full-sized image')
    ],
    thumbnail_speccy, #callback
)

register(
    'file-zxspectrum-save', #name
    'save a ZX-Spectrum image (.scr) file', #description
    'save a ZX-Spectrum image (.scr) file',
    'Юрий Шаповалов (urishap@mail.ru) based on Juan J. Martinez code', #author
    'Юрий Шаповалов (urishap@mail.ru) based on Juan J. Martinez code', #copyright
    '2022', #year
    'ZX-Spectrum',
    '*',
    [   #input args. Format (type, name, description, default [, extra])
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
        (PF_STRING, "filename", "The name of the file", None),
        (PF_STRING, "raw-filename", "The name of the file", None),
    ],
    [], #results. Format (type, name, description)
    save_speccy, #callback
    on_query = register_save_handlers,
    menu = '<Save>'
)

register(
    'file-zxspectrum-load', #name
    'load a ZX-Spectrum image (.scr) file', #description
    """load a ZX-Spectrum image (.scr) file, generated from a video-map dump:
    a 6912 byte file 256x192 monochrome pixels + 768 bytes of color information.""",
    'João S. O. Bueno', #author
    'João S. O. Bueno', #copyright
    '2017', #year
    'ZX-Spectrum',
    None, #image type
    [   #input args. Format (type, name, description, default [, extra])
        (PF_STRING, 'filename', 'The name of the file to load', None),
        (PF_STRING, 'raw-filename', 'The name entered', None),
    ],
    [(PF_IMAGE, 'image', 'Output image')], #results. Format (type, name, description)
    load_speccy, #callback
    on_query = register_load_handlers,
    menu = "<Load>",
)


main()
