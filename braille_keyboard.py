#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
Description.

R Jeffery
Date
'''

import pyglet


class BrailleApp(pyglet.window.Window):
    def __init__(self):
        super().__init__(width=640, height=480)

        self.batch = pyglet.graphics.Batch()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)

        self.unicode_offset = int('0x2800', 16) # Six-dot Braille characters start at U+2800
        self.braille_keys = {102:1,
                             100:2,
                             115:3,
                             106:4,
                             107:5,
                             108:6,
                             97:'left',
                             59:'right',
                             32:'space'}
        self.key_buffer = []
        self.cell_value = 0 # Treat the cell like a binary number; "c" (1,4) is 2^0 + 2^3 = 9

        self.cursor = [0, 0]
        self.line = ''
        self.document = []

    def on_key_press(self, symbol, modifiers):
        if symbol in self.braille_keys:
            key = self.braille_keys[symbol]
            #print(key, 'down')
            self.key_buffer.append(key)
            if type(key) == int:
                self.cell_value += 2 ** (key - 1)

    def on_key_release(self, symbol, modifiers):
        if symbol in self.braille_keys:
            key = self.braille_keys[symbol]
            #print(key, 'up')
            self.key_buffer.remove(key)

            # Once all keys are released, add a character.
            if len(self.key_buffer) < 1:
                #print(chr(self.cell_value + self.unicode_offset))
                self.line += chr(self.cell_value + self.unicode_offset)
                self.cell_value = 0
                self.cursor[0] += 1
                if len(self.line) >= 40:
                    self.document.append(self.line)
                    self.cursor[1] += 1
                    self.line = ''
                    self.cursor[0] = 0

    def on_draw(self):
        width, height = self.get_size()

        # Draw foreground and background.
        self.batch.add(4, pyglet.gl.GL_QUADS, self.background,
                ('v2i', (0,     0,
                         0,     height,
                         width, height,
                         width, 0)),
                ('c3B', (240,) * 12))

        text = '\n'.join(self.document + [self.line])
        pyglet.text.Label(text=text,
                          font_size=12,
                          color=(0, 0, 0, 255),
                          x=0, y=height,
                          width=width,
                          height=height,
                          anchor_x='left',
                          anchor_y='top',
                          multiline=True,
                          batch=self.batch,
                          group=self.foreground)


        # Render and reset.
        self.batch.draw()
        self.batch = pyglet.graphics.Batch()

    def on_exit(self):
        exit()

    def run(self):
        pyglet.app.run()

def main():
    application = BrailleApp()
    application.run()


# Only call main if program is run directly (not imported).
if __name__ == "__main__":
    from sys import version
    print('Running with Python', version) # Double-check the version.

    main()
