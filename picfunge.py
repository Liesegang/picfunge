#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed by Curtis McEnroe (programble@gmail.com) under ISC License

import sys

from optparse import OptionParser
from PIL import Image

import boards

__version__ = "0.2.0"


def main():
    parser = OptionParser(usage="%prog [options] [file]")
    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False, help="Turn on debugging mode")
    parser.add_option("--delay", dest="debugdelay", action="store", type="int", default=-1, help="Delay in milliseconds between each step in debugging mode, or -1 to wait for input")
    parser.add_option("-x", "--x", dest="x", action="store", type="int", default=0, help="Initial X coordinate")
    parser.add_option("-y", "--y", dest="y", action="store", type="int", default=0, help="Initial Y coordinate")
    parser.add_option("--version", dest="version", action="store_true", default=False, help="Show version information and exit")
    (options, args) = parser.parse_args()
    
    if options.version:
        print("befungee", __version__)
        return 0
    
    # Default to reading from stdin
    if len(args) == 0:
        print("No input file")
        return 1

    # Read in file
    try:
        image = Image.open(args[0], 'r')
    except IOError:
        print("Could not open file")
        return 1
    
    width, height = image.size

    board = boards.Befunge93Board(width, height, options.debug, options.debugdelay)
    board.pointer.x, board.pointer.y = options.x, options.y

    for y in range(height):
        for x in range(width):
            # getpixel((x,y))で左からx番目,上からy番目のピクセルの色を取得し、img_pixelsに追加する
            [r, g, b] = image.getpixel((x,y))[0:3]
            board.put(x, y, 0, r)
            board.put(x, y, 1, g)
            board.put(x, y, 2, b)

    
    image.close()
    
    # Run the program
    while not board.dead():
        #try:
            board.step()
        # except Exception as ex:
        #     # Make sure stdout is not redirected
        #     sys.stdout = sys.__stdout__
        #     print("Error (%d,%d):" % (board.pointer.x, board.pointer.y), ex)
        #     return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
