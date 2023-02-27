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
# UriS: 
# add save .spr,
# add color (255, 127, 0) as an invisible color
# ----------------------------------------------

from __future__ import print_function

from gimpfu import *
from os import name as os_name
from sys import stderr as sys_stderr

# SIZE = WIDTH, HEIGHT = 256, 192

# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
# orange for invisible pixels
# INVISIBLE = (255, 127, 0) 

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

def save_sprites(img, drawable, filename, raw_filename, foo, isattr, isbfi, numX, numY):
    number=int(numX*numY)
    h = pdb.gimp_drawable_height(drawable)
    w = pdb.gimp_drawable_width(drawable)
#    if w != 256 or h != 192:
    if (numX*8)>w or (numY*8)>h:
        pdb.gimp_message("Sprite area must be not bigger image size")
        return
    w=int(numX*8)
    h=int(numY*8)
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
            if isbfi and (C2I[attr[0]] > C2I[attr[1]]):
                attr[0], attr[1] = attr[1], attr[0]
                byte = [~b & 0xff for b in byte]

            if not(isbfi) and (C2I[attr[0]] < C2I[attr[1]]):
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



    texta="; Sprites data ======================\n"
    for n in range(0,int(number)):
        texta+="\nDEFB "
        for i in range(0,8):
            texta+="%{0:08b}".format(int(pixels[n*8+i]))
            if i<7:
                texta+=","
        texta+=" ; {0:03d}".format(n)
    if isattr:
        texta+="\n\n; Attributes data ======================"
        texta+="\n;      fIgrbGRB"
        for n in range(0,int(number)):
            texta+="\nDEFB "
            texta+="%{0:08b}".format(int(attrib[n]))
            texta+=" ; {0:03d}".format(n)
    texta+="\n\n; End of data ======================\n"
#    texta+="\nIsBFI="+isbfi

    with open(filename, "w") as fh:
        fh.write(texta)

#    with open(filename, "wb") as fh:
#        fh.write(bytearray(pixels))
#        fh.write(bytearray(attrib))

# ===============================================================================


def register_save_handlers():
    gimp.register_save_handler('file-zxsprites-save', 'spr', '')

register(
    'file-zxsprites-save', #name
    'save a ZX-Spectrum sprites (.spr) file', #description
    'save a ZX-Spectrum sprites (.spr) file',
    'Юрий Шаповалов (urishap@mail.ru) based on Juan J. Martinez code', #author
    'Юрий Шаповалов (urishap@mail.ru) based on Juan J. Martinez code', #copyright
    '2023', #year
    'ZX-Spectrum-spr',
    '*',
    [
        (PF_IMAGE, "image", "Input image", None), #
        (PF_DRAWABLE, "drawable", "Input drawable", None), #
        (PF_STRING, "filename", "The name of the file", None), #
        (PF_STRING, "raw_filename", "The name of the file", None), #
        (PF_TOGGLE, "foo", "Destroy all Klingns:", 0),
        (PF_TOGGLE, "isattr", "Write attributes:", 1), #
        (PF_TOGGLE, "isbfi", "Light color is ink:", 1), #
        (PF_SPINNER, "numX", "Wide of sprites area:", 32, (1, 32, 1)), #
        (PF_SPINNER, "numY", "Height of sprites area:", 24, (1, 24, 1)), #
    ],
    [], #results. Format (type, name, description)
    save_sprites, #callback
    on_query = register_save_handlers,
    menu = "<Save>"
)

main()

