#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import random
import sys
import time

from io import StringIO

from funge import Pointer

def visible(i):
    if(0x20 <= i and i <= 0x7e):
        return chr(i)
    else:
        return hex(i) + " "

class Befunge93Board:
    """A Befunge-93 board"""
    def __init__(self, width, height, debug=False, debug_delay=-1):
        self.pointer = Pointer()
        self._list = [[[0] * width for i in range(height)] for j in range(3)]

        self.width = width
        self.height = height

        self.debug = debug
        self.debug_delay = debug_delay
        self.debugstream = StringIO()
    
    def get(self, x, y, z):
        # Return space if out of bounds
        if x >= self.width or y >= self.height or z >= 3 or x < 0 or y < 0 or z < 0:
            return 0
        return self._list[z][y][x]
    
    def put(self, x, y, z, value):
        # Ignore if out of bounds
        if x >= self.width or y >= self.height or z >= 3 or x < 0 or y < 0 or z < 0:
            return
        self._list[z][y][x] = value
    
    def step(self):
        if self.debug:
            # Redirect output for debugging
            sys.stdout = self.debugstream
        
        c = self.get(self.pointer.x, self.pointer.y, self.pointer.z)
        if c == ord('"'):
            self.pointer.stringmode = not self.pointer.stringmode
        elif self.pointer.stringmode:
            self.push(c)
        elif c in map(ord,"0123456789"):
            self.push(c - ord('0'))
        elif c == ord('>'):
            self.pointer.dx = 1
            self.pointer.dy = 0
        elif c == ord('<'):
            self.pointer.dx = -1
            self.pointer.dy = 0
        elif c == ord('^'):
            self.pointer.dx = 0
            self.pointer.dy = -1
        elif c == ord('v'):
            self.pointer.dx = 0
            self.pointer.dy = 1
        elif c == ord('?'):
            dir = ['>', 'v', '<', '^'][random.randint(0, 3)]
            if dir == '>':
                self.pointer.dx = 1
                self.pointer.dy = 0
            elif dir == '<':
                self.pointer.dx = -1
                self.pointer.dy = 0
            elif dir == '^':
                self.pointer.dx = 0
                self.pointer.dy = -1
            elif dir == 'v':
                self.pointer.dx = 0
                self.pointer.dy = 1
        elif c == ord('+'):
            self.push(self.pop() + self.pop())
        elif c == ord('*'):
            self.push(self.pop() * self.pop())
        elif c == ord('-'):
            a = self.pop()
            b = self.pop()
            self.push(b - a)
        elif c == ord('/'):
            a = self.pop()
            b = self.pop()
            self.push(b / a)
        elif c == ord('%'):
            a = self.pop()
            b = self.pop()
            self.push(b % a)
        elif c == ord('!'):
            x = self.pop()
            if x == 0:
                self.push(1)
            else:
                self.push(0)
        elif c == ord('`'):
            a = self.pop()
            b = self.pop()
            if b > a:
                self.push(1)
            else:
                self.push(0)
        elif c == ord('_'):
            x = self.pop()
            if x == 0:
                self.pointer.dx = 1
                self.pointer.dy = 0
            else:
                self.pointer.dx = -1
                self.pointer.dy = 0
        elif c == ord('|'):
            x = self.pop()
            if x == 0:
                self.pointer.dx = 0
                self.pointer.dy = 1
            else:
                self.pointer.dx = 0
                self.pointer.dy = -1
        elif c == ord(':'):
            x = self.pop()
            self.push(x)
            self.push(x)
        elif c == ord('\\'):
            a = self.pop()
            b = self.pop()
            self.push(a)
            self.push(b)
        elif c == ord('$'):
            self.pop()
        elif c == ord('.'):
            x = self.pop()
            sys.stdout.write(str(x) + ' ')
        elif c == ord(','):
            x = self.pop()
            sys.stdout.write(chr(x))
        elif c == ord('#'):
            self.pointer.move()
        elif c == ord('p'):
            y = self.pop()
            x = self.pop()
            v = self.pop()
            self.put(x, y, self.pointer.z, v)
        elif c == ord('g'):
            y = self.pop()
            x = self.pop()
            self.push(self.get(x, y, self.pointer.z))
        elif c == ord('P'):
            z = self.pop()
            y = self.pop()
            x = self.pop()
            v = self.pop()
            self.put(x, y, z, v)
        elif c == ord('G'):
            z = self,pop()
            y = self.pop()
            x = self.pop()
            self.push(self.get(x, y, z))
        elif c == ord('&'):
            x = sys.stdin.read(1)
            try:
                self.push(int(x))
            except ValueError:
                self.push(-1)
        elif c == ord('~'):
            x = sys.stdin.read(1)
            if x == '':
                self.push(-1)
            else:
                self.push(ord(x))
        elif c == ord('s'):
            y = self.pop()
            x = self.pop()
            self.pointer.px = x
            self.pointer.py = y
        elif c == ord('S'):
            z = self.pop()
            y = self.pop()
            x = self.pop()
            self.pointer.px = x
            self.pointer.py = y
            self.pointer.pz = z
        elif c == ord('@'):
            self.pointer.dx = 0
            self.pointer.dy = 0
        elif c == ord('A'):
            self.pointer.z += 1
            self.pointer.z %= 3
        elif c == ord('V'):
            self.pointer.z -= 1
            self.pointer.z %= 3
        elif c == ord('M'):
            self.pointer.pz += 1
            self.pointer.pz %= 3
        elif c == ord('W'):
            self.pointer.pz -= 1
            self.pointer.pz %= 3
        
        # Advance pointer
        if not c in map(ord, "VA"):
            self.pointer.move()
        
        # Wrap-around
        if self.pointer.x >= self.width:
            self.pointer.x -= self.width
        elif self.pointer.x <= -1:
            self.pointer.x += self.width
        elif self.pointer.y >= self.height:
            self.pointer.y -= self.height
        elif self.pointer.y <= -1:
            self.pointer.y += self.height
        
        # Print debugging information
        if self.debug:
            # Reset debugging output redirection
            sys.stdout = sys.__stdout__
            # Clear screen
            if os.name == "posix":
                sys.stdout.write("\x1b[H\x1b[2J")
            print("Pointer: x=%d y=%d z=%d pz=%d py=%d pz=%d dx=%d dy=%d stringmode=%s" % (self.pointer.x, self.pointer.y, self.pointer.z, self.pointer.px, self.pointer.py, self.pointer.pz, self.pointer.dx, self.pointer.dy, self.pointer.stringmode))
            print("Board:")
            for z in range(3):
                sys.stdout.write(["r","g","b"][z] + "-----------------\n")
                for y in range(self.height):
                    for x in range(self.width):
                        c = self.get(x, y, z)
                        if x == self.pointer.x and y == self.pointer.y and z == self.pointer.z:
                            if os.name == "posix":
                                sys.stdout.write("\033[41m")
                        elif x == self.pointer.px and y == self.pointer.py and z == self.pointer.pz:
                            if os.name == "posix":
                                sys.stdout.write("\033[41m")
                        sys.stdout.write(visible(c))
                        if os.name == "posix":
                            sys.stdout.write("\033[0m")
                    sys.stdout.write('\n')
            print("Output:")
            self.debugstream.seek(0)
            print(self.debugstream.read())
            if self.debug_delay == -1:
                sys.stdin.read(1)
            else:
                time.sleep(self.debug_delay / 1000.0)
    def dead(self):
        return self.pointer.dx == 0 and self.pointer.dy == 0

    def push(self, value):
        self.put(self.pointer.px, self.pointer.py, self.pointer.pz, value)
        self.pointer.px += 1
        if(self.pointer.px == self.width):
            self.pointer.px = 0
            self.pointer.py += 1
            self.pointer.py %= self.height

    def pop(self):
        self.pointer.px -= 1
        if(self.pointer.px == -1):
            self.pointer.px = self.width - 1
            self.pointer.py -= 1
            self.pointer.py %= self.height
        return self.get(self.pointer.px, self.pointer.py, self.pointer.pz)

        return ret

