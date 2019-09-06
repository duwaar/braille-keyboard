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
                32:'space',
                65505:'l-shift'
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

        self.line_length = 40
        self.font_size = 12
        self.cursor_position = 0
        self.write_mode = 'insert'

        self.file_name = 'braille_notes.txt'
        self.document = self.load_file()

    def on_key_press(self, symbol, modifiers):
        if symbol in self.braille_keys:
            key = self.braille_keys[symbol]
            self.key_buffer.append(key)
            if type(key) == int:
                self.current_cell[key] = True

    def on_key_release(self, symbol, modifiers):
        if symbol not in self.braille_keys:
            return 0

        key = self.braille_keys[symbol]
        assert key in self.key_buffer,\
                'Cannot remove {}. Not in key buffer: {}'.format(key, self.key_buffer)
        self.key_buffer.remove(key)

        self.key_function(key)
        self.generate_character()

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
        doc_text = self.generate_doc_text()
        pyglet.text.Label(
                text=doc_text,
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
        cursor_x = self.cursor_position % self.line_length * font_width - cursor_width // 2
        cursor_y = window_height - (self.cursor_position // self.line_length + 1) * font_height
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
        bar =        'cursor: ' + str(self.cursor_position)\
                + ' | lines: ' + str(len(self.document) // self.line_length + 1)\
                + ' | mode: ' + self.write_mode\
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

    def on_close(self):
        self.save_file()
        exit()

    def run(self):
        pyglet.app.run()

    def load_file(self):
        ''' Returns array of characters in file. '''
        file = open(self.file_name, 'r')
        text = file.read()
        document = list(text)
        file.close()
        return document

    def save_file(self):
        ''' Writes all characters to file. '''
        file = open(self.file_name, 'w')
        text = self.generate_doc_text()
        file.write(text)
        file.close()

    def generate_doc_text(self):
        ''' Convert the array of lines into a block of text. '''
        doc_text = ''
        for line in range(len(self.document) // self.line_length + 1):
            line_start = line * self.line_length
            line_end = line_start + self.line_length
            for char in self.document[line_start:line_end]:
                doc_text += char
            doc_text += '\n'
        return doc_text

    def get_cell_value(self):
        ''' Calculate the "value" of the Braille cell in decimal (if each dot is a bit). '''
        value = 0
        for dot in self.current_cell:
            value += 2 ** (dot - 1) if self.current_cell[dot] == True else 0
        return value

    def key_function(self, key):
        ''' Respond to a non-character key input. '''
        if key == 'space':
            self.write_cell(self.cursor_position, 0)
        elif key == 'right' and self.cursor_to_end() > 0:
            self.cursor_position += 1
        elif key == 'left' and self.cursor_position != 0:
            self.cursor_position -= 1
        elif key == 'up' and self.cursor_line() > 0:
            self.cursor_position -= self.line_length
        elif key == 'down' and self.cursor_to_end() >= self.line_length:
            self.cursor_position += self.line_length
        elif key == 'l-shift':
            if self.write_mode == 'insert':
                self.write_mode = 'assign'
            elif self.write_mode == 'assign':
                self.write_mode = 'delete'
            elif self.write_mode == 'delete':
                self.write_mode = 'insert'
            else:
                assert False, 'Write mode "{}" invalid.'.format(self.write_mode)
        elif key == 'open' and 'l-ctrl' in self.key_buffer:
            pass
        elif key == 'save' and 'l-ctrl' in self.key_buffer:
            pass
        elif key == 'help' and 'l-ctrl' in self.key_buffer:
            pass
        elif key == 'pref' and 'l-ctrl' in self.key_buffer:
            pass

    def generate_character(self):
        ''' Once all keys are released, generate a character. '''
        value = self.get_cell_value()
        if len(self.key_buffer) < 1 and value > 0:
            self.write_cell(self.cursor_position, value)
            for dot in self.current_cell:
                self.current_cell[dot] = False

    def write_cell(self, index, value):
        ''' Assign or insert unicode character "value" at "index" depending on current mode. '''
        if self.write_mode == 'insert':
            self.document.insert(index, chr(value + self.unicode_offset))
            self.cursor_position += 1
        elif self.write_mode == 'assign' and self.cursor_position <= len(self.document) - 1:
            self.document[index] = chr(value + self.unicode_offset)
            self.cursor_position += 1
        elif self.write_mode == 'delete'\
                and value == 0\
                and self.cursor_position <= len(self.document) - 1:
            self.document.pop(self.cursor_position)

    def cursor_line(self):
        ''' Return the line number the cursor is on. '''
        return self.cursor_position // self.line_length

    def cursor_char(self):
        ''' Return the position of the cursor on the line. '''
        return self.cursor_position % self.line_length

    def cursor_to_end(self):
        ''' Return the number of characters from the cursor to the last index. '''
        return len(self.document) - self.cursor_position


def main():
    application = BrailleApp()
    application.run()


# Only call main if program is run directly (not imported).
if __name__ == "__main__":
    from sys import version
    print('Running with Python', version) # Double-check the version.

    main()
