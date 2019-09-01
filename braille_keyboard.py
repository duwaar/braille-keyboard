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
                103:'down',
                104:'up',
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

        self.cursor_char = 0
        self.cursor_line = 0
        self.blank_line = [chr(0 + self.unicode_offset)] * 40 + ['\n']
        self.document = [self.blank_line.copy()] # Start document with one blank line.
        self.font_size = 12

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

    def on_key_release(self, symbol, modifiers):
        if symbol not in self.braille_keys:
            return 0

        key = self.braille_keys[symbol]
        #print(key, 'up')
        assert key in self.key_buffer,\
                'Cannot remove {}. Not in key buffer: {}'.format(key, self.key_buffer)
        self.key_buffer.remove(key)

        # Once all keys are released, generate a character.
        value = self.get_cell_value()
        if len(self.key_buffer) < 1 and value > 0:
            #print(chr(value + self.unicode_offset))
            self.document[self.cursor_line][self.cursor_char] = chr(value + self.unicode_offset)
            self.cursor_char += 1
            for dot in self.current_cell:
                self.current_cell[dot] = False

        # Respond to a non-character key input.
        if key == 'space':
            self.document[self.cursor_line][self.cursor_char] = chr(0 + self.unicode_offset)
            self.cursor_char += 1
        elif key == 'right':
            self.cursor_char += 1
        elif key == 'left':
            self.cursor_char -= 1
        elif key == 'up' and self.cursor_line > 0:
            self.cursor_line -= 1
        elif key == 'down':
            self.cursor_line += 1

        # Change lines if we go off the end of the current one.
        if self.cursor_char > 40:
            self.cursor_line += 1
            self.cursor_char = 0
        elif self.cursor_char < 0 and self.cursor_line > 0:
            self.cursor_line -= 1
            self.cursor_char = 40

        # Add a new line if necessary.
        if self.cursor_line > len(self.document) - 1:
            self.document.append(self.blank_line.copy())

        #print(self.cursor_char, self.cursor_line)

    def on_draw(self):
        window_width, window_height = self.get_size()

        # Draw background color.
        self.batch.add(
                4,
                pyglet.gl.GL_QUADS,
                self.background,
                ('v2i', (
                    0,              0,
                    0,              window_height,
                    window_width,   window_height,
                    window_width,   0
                    )),
                ('c3B', (240,) * 12)
                )

        # Draw Braille document text.
        display_text = ''
        for line in self.document:
            for char in line:
                display_text += char
        pyglet.text.Label(
                text=display_text,
                font_size=self.font_size,
                color=(0, 0, 0, 255),
                x=0,
                y=window_height,
                width=window_width,
                height=window_height,
                anchor_x='left',
                anchor_y='top',
                multiline=True,
                batch=self.batch,
                group=self.foreground
                )

        # Draw cursor line.
        font_width  = self.font_size * (1)
        font_height = round(self.font_size * 1.25) + 4
        cursor_width = 2
        cursor_height = font_height
        cursor_x = self.cursor_char * font_width - cursor_width // 2
        cursor_y = window_height - (self.cursor_line + 1) * font_height
        self.batch.add(
                4,
                pyglet.gl.GL_QUADS,
                self.foreground,
                ('v2i', (
                    cursor_x,                   cursor_y,
                    cursor_x,                   cursor_y + cursor_height,
                    cursor_x + cursor_width,    cursor_y + cursor_height,
                    cursor_x + cursor_width,    cursor_y
                    )),
                ('c3B', (0,) * 12)
                )

        # Draw status bar.
        bar = 'cursor: ' + str(self.cursor_char) + ',' + str(self.cursor_line)\
                + ' | lines: ' + str(len(self.document))\
                + ' | keys: ' + str(self.key_buffer)\
                + ' | font: ' + str(self.font_size) + 'pt., '\
                + str(font_width) + 'px., '\
                + str(font_height) + 'px.'
        pyglet.text.Label(
                text=bar,
                font_size=self.font_size,
                multiline=False,
                color=(0, 0, 0, 255),
                x=0,
                y=0,
                anchor_x='left',
                anchor_y='bottom',
                batch=self.batch,
                group=self.foreground
                )


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
