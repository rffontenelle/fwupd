#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Peter Jones <pjones@redhat.com>
# Copyright (C) 2020 Richard Hughes <richard@hughsie.com>
#
# SPDX-License-Identifier: LGPL-2.1+
#
# pylint: disable=wrong-import-position,too-many-locals,unused-argument, too-many-statements
# pylint: disable=invalid-name,too-many-instance-attributes, missing-module-docstring

import os
import sys
import argparse
import gettext
import math
import io
import gzip
import cairo
import gi
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Pango, PangoCairo
from PIL import Image

class Rasterizer:
    """ Rasterize some text """

    def __init__(self, label, modir, linguas):
        self.text = label
        self.modir = modir
        while modir.endswith('/'):
            modir = modir[:-1]
        self.linguas = linguas
        self.directory = modir
        self.domain = "fwupd"
        self.font_face = "sans-serif"
        self.pattern = "{directory}/{language}/LC_IMAGES/fwupd-{width}-{height}.{suffix}"

        gettext.textdomain(self.domain)
        gettext.install(self.domain, self.modir)

    @property
    def languages(self):
        """ Find all of our languages """
        for x in open(self.linguas, "r").readlines():
            x = x.strip()
            # currently ligatures seem completely broken in hi, and I don't know
            # why.  They get LANG=C.
            if x == 'hi':
                continue
            yield x
        yield "en"

    def render(self):
        """ Do the work... """
        def render_one(language, string, width, height, filename):
            """ Do the work... """

            font_desc = "Sans %fpx" % (height / 32,)
            fd = Pango.FontDescription(font_desc)
            font_option = cairo.FontOptions()
            font_option.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
            l = Pango.Language.from_string(language)

            img = cairo.ImageSurface(cairo.FORMAT_RGB24, 1, 1)
            cctx = cairo.Context(img)
            layout = PangoCairo.create_layout(cctx)
            pctx = layout.get_context()
            pctx.set_font_description(fd)
            pctx.set_language(l)
            fs = pctx.load_fontset(fd, l)
            PangoCairo.context_set_font_options(pctx, font_option)

            attrs = Pango.AttrList()
            length = len(bytes(string, "utf8"))
            items = Pango.itemize(pctx, string, 0, length, attrs, None)
            gs = Pango.GlyphString()
            Pango.shape(string, length, items[0].analysis, gs)
            del img, cctx, pctx, layout

            def find_size(fs, f, data):
                """ find our size, I hope... """
                (ink, log) = gs.extents(f)
                if ink.height == 0 or ink.width == 0:
                    return False
                data.update({"log": log, "ink": ink})
                return True
            data = {}
            fs.foreach(find_size, data)

            if len(data) == 0:
                print("Missing sans fonts")
                sys.exit(2)
            log = data['log']
            ink = data['ink']

            height = math.ceil(max(ink.height, log.height) / Pango.SCALE)
            width = math.ceil(max(ink.width, log.width) / Pango.SCALE)

            x = -math.ceil(log.x / Pango.SCALE)
            y = -math.ceil(log.y / Pango.SCALE)

            img = cairo.ImageSurface(cairo.FORMAT_RGB24, width, height)
            cctx = cairo.Context(img)
            layout = PangoCairo.create_layout(cctx)
            pctx = layout.get_context()
            PangoCairo.context_set_font_options(pctx, font_option)

            cctx.set_source_rgb(1, 1, 1)
            cctx.move_to(x, y)
            def do_write(fs, f, data):
                """ write out glyphs """
                ink = gs.extents(f)[0]
                if ink.height == 0 or ink.width == 0:
                    return False
                PangoCairo.show_glyph_string(cctx, f, gs)
                return True
            fs.foreach(do_write, None)
            img.flush()
            try:
                tmpname = filename[len(os.environ['DESTDIR']):]
            except KeyError:
                tmpname = filename[len(os.environ['MESON_BUILD_ROOT']):]
            print("Writing {}".format(tmpname))
            def make_dir(d):
                """ make our parent dir and then our own dir """
                if os.access(d, os.O_RDWR):
                    return
                parts = os.path.split(d)
                if parts and parts[0]:
                    make_dir(parts[0])
                os.mkdir(d, 0o755)
            d = os.path.split(filename)[0]
            make_dir(d)

            # write PNG
            with io.BytesIO() as io_png:
                img.write_to_png(io_png)
                io_png.seek(0)

                # convert to BMP
                with io.BytesIO() as io_bmp:
                    pimg = Image.open(io_png)
                    pimg.save(io_bmp, format='BMP')
                    io_bmp.seek(0)
                    with gzip.open(filename, 'wb') as f:
                        f.write(io_bmp.read())

        for lang in self.languages:
            #print("lang:\"%s\" string:\"%s\"" % (lang, string))
            # these are the 1.6:1 of some common(ish) screen widths
            sizes = ((640, 480), (800, 600), (1024, 768), (1920, 1080),
                     (3840, 2160), (5120, 2880), (5688, 3200), (7680, 4320))
            nameinfo = {
                'directory': self.directory,
                'language': lang,
            }
            if lang == 'en':
                string = self.text
            else:
                tl = gettext.translation(self.domain, self.modir,
                                         languages=[lang])
                string = tl.gettext(self.text)
                if string == self.text:
                    continue
            for width, height in sizes:
                nameinfo.update({'width': width,
                                 'height': height,
                                 'suffix': 'bmp.gz'})
                filename = self.pattern.format_map(nameinfo)
                if not os.path.exists(filename):
                    render_one(lang, string, width, height, filename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make UX images')
    parser.add_argument('--localedir', help='Locale dir', required=True)
    parser.add_argument('--label', help='Update text', required=True)
    parser.add_argument('--linguas', help='LINGUAS location', required=True)
    args = parser.parse_args()
    r = Rasterizer(label=args.label, modir=args.localedir, linguas=args.linguas)
    r.render()
