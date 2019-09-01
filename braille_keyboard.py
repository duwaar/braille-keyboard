#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
'''
A notepad-like application for editing Braille text files. Useful for helping sighted people learn
Braille.

31 August 2019
'''

import pyglet


class BrailleApp(pyglet.window.Window):
    def __init__(self):
        # Create a window with the caption "Braille Notepad".
        super().__init__(
                width=640, height=480,
                caption='\u2820\u2803\u2817\u2801\u280a\u2807\u2807\u2811'\
                        + '\u2800\u2820\u281d\u2815\u281e\u2811\u280f\u2801\u2819')

        self.batch = pyglet.graphics.Batch()
        self.background = pyglet.graphics.OrderedGroup(0)
        self.foreground = pyglet.graphics.OrderedGroup(1)

        self.unicode_offset = int('0x2800', 16) # Six-dot Braille characters start at U+2800
        self.braille_keys = {
                102:1,
                100:2,
                115:3,
                106:4,
                107:5,
                108:6,
                97:'left',
                59:'right',
                32:'space'
                }
        self.current_cell = {
                1:False,
                2:False,
                3:False,
                4:False,
                5:False,
                6:False
                }
        self.key_buffer = []
        self.special_keys = []
        self.cursor = [0, 0]
        self.blank_line = [chr(0 + self.unicode_offset)] * 40 + ['\n']
        self.document = [self.blank_line.copy()] # Start document with one blank line.

    def get_cell_value(self):
        value = 0
        for dot in self.current_cell:
            value += 2 ** (dot - 1) if self.current_cell[dot] == True else 0
        return value

    def on_key_press(self, symbol, modifiers):
        if symbol in self.braille_keys:
            key = self.braille_keys[symbol]
            #print(key, 'down')
            self.key_buffer.append(key)
            if type(key) == int:
                self.current_cell[key] = True
            else:
                self.special_keys.append(key)

    def on_key_release(self, symbol, modifiers):
        if symbol in self.braille_keys:
            key = self.braille_keys[symbol]
            #print(key, 'up')
            self.key_buffer.remove(key)

        # Once all keys are released, process the input.
        if len(self.key_buffer) < 1:
            # Add characters...
            value = self.get_cell_value()
            if value > 0:
                #print(chr(value + self.unicode_offset))
                self.document[self.cursor[1]][self.cursor[0]] = chr(value + self.unicode_offset)
                self.cursor[0] += 1
                for dot in self.current_cell:
                    self.current_cell[dot] = False
            # ...and/or move the cursor.
            else:
                for key in self.special_keys:
                    if key == 'space':
                        self.document[self.cursor[1]][self.cursor[0]] = chr(0 + self.unicode_offset)
                        self.cursor[0] += 1
                    elif key == 'right':
                        self.cursor[0] += 1
                    elif key == 'left':
                        self.cursor[0] -= 1
                    self.special_keys.remove(key)

            # Change lines if we go off the end of the current one.
            if self.cursor[0] > 40:
                self.cursor[1] += 1
                self.cursor[0] = 0
                # Add a new line if necessary.
                if self.cursor[1] > len(self.document) - 1:
                    self.document.append(self.blank_line.copy())
            elif self.cursor[0] < 0:
                self.cursor[1] -= 1
                self.cursor[0] = 40

        #print(self.cursor)

    def on_draw(self):
        width, height = self.get_size()

        # Draw background color.
        self.batch.add(4, pyglet.gl.GL_QUADS, self.background,
                ('v2i', (0,     0,
                         0,     height,
                         width, height,
                         width, 0)),
                ('c3B', (240,) * 12))

        # Draw Braille document text.
        display_text = ''
        for line in self.document:
            for char in line:
                display_text += char
            display_text += '\n'
        pyglet.text.Label(text=display_text,
                          font_size=18,
                          color=(0, 0, 0, 255),
                          x=0, y=height,
                          width=width,
                          height=height,
                          anchor_x='left',
                          anchor_y='top',
                          multiline=True,
                          batch=self.batch,
                          group=self.foreground)

        # Draw status bar.
        bar = 'cursor: ' + str(self.cursor)\
                + ' | lines: ' + str(len(self.document))
        pyglet.text.Label(text=bar,
                          font_size=12,
                          multiline=False,
                          color=(0, 0, 0, 255),
                          x=0,
                          y=0,
                          anchor_x='left',
                          anchor_y='bottom',
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
