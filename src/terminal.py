import imgui
import imguihelper
import os
import _nx
import runpy
import sys
from imgui.integrations.nx import NXRenderer
from nx.utils import clear_terminal
from io import StringIO
import contextlib
import logging

sys.argv = [""]  # workaround needed for runpy

@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old

class Terminal():
    def colorToFloat(self, t):
        nt = ()
        for v in t:
            nt += ((1 / 255) * v,)
        return nt

    def __str__(self):
        return "Terminal for the switch, made by PuffDip"

    def __init__(self):
        logging.basicConfig(filename='src/terminal.log', format='%(levelname)s:%(message)s', level=logging.ERROR)
        # (r, g, b)
        self.KEY_COLOR = self.colorToFloat((230, 126, 34))
        self.KEY_FUNC_COLOR = self.colorToFloat((196, 107, 29))

        self.TILED_DOUBLE = 1

        self.renderer = NXRenderer()
        self.currentDir = os.getcwd()

        self.CONSOLE_TEXT = "None"
        self.version_number = '0.1'
        self.keyboard_toggled = False
        self.user_input = ""
        self.CAPS = False
        self.SYS = False
        self.command = 'Please, type your command here.'

        self.keyboard = [
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '='],
            ['TAB', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']'],
            ['SYS', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', '\'', '\\'],
            ['SHIFT', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/']
        ]

        self.sys_keyboard = [
            ['~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+'],
            ['TAB', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '{', '}'],
            ['SYS', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ':', '"', '|'],
            ['SHIFT', 'z', 'x', 'c', 'v', 'b', 'n', 'm', '<', '>', '?']
        ]

    def run_python_module(self, path: str):
        # clear both buffers
        imguihelper.clear()
        imguihelper.clear()
        _nx.gfx_set_mode(self.TILED_DOUBLE)
        clear_terminal()
        runpy.run_path(path, run_name='__main__')
        # _nx.gfx_set_mode(LINEAR_DOUBLE)
        imguihelper.initialize()

    def shift_key(self):
        if self.CAPS:
            self.CAPS = False
        else:
            self.CAPS = True

    def sys_key(self):
        if self.SYS:
            self.SYS = False
        else:
            self.SYS = True

    def keyboard_key(self, key:str, same_line=False, *, default:str=None, color=None):
        if same_line:
            imgui.same_line()

        if self.CAPS:
            key = key.upper()

        if color is None:
            color = self.KEY_COLOR

        imgui.push_style_color(imgui.COLOR_BUTTON, *color)
        if imgui.button(key, width=60, height=60):
            if default is None:
                if self.command == 'Please, type your command here.':
                    self.command = key
                else:
                    self.command = self.command + key
            elif default == 'SHIFT':
                self.shift_key()
            elif default == 'SYS':
                self.sys_key()
            elif default == 'TAB':
                self.command = self.command + '    '

        imgui.pop_style_color(1)

    def main(self):
        while True:
            self.renderer.handleinputs()
            imgui.new_frame()

            self.width, self.height = self.renderer.io.display_size
            imgui.set_next_window_size(self.width, self.height)
            imgui.set_next_window_position(0, 0)
            # Header
            imgui.begin("",
                        flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE | imgui.WINDOW_NO_SAVED_SETTINGS
                        )

            imgui.text("PyNx Terminal By PuffDip" + " - V" + str(self.version_number))

            # Body
            if self.keyboard_toggled:
                imgui.begin_child("region", -5, -480, border=True)
            else:
                imgui.begin_child("region", -5, -120, border=True)
            imgui.text(self.CONSOLE_TEXT)
            imgui.end_child()

            imgui.begin_group()
            # Keyboard
            try:
                if self.keyboard_toggled:
                    if self.SYS:
                        keyboard = self.sys_keyboard
                    else:
                        keyboard = self.keyboard

                    for rows in keyboard:
                        for row in rows:
                            if row == 'TAB' or row == 'SYS' or row == 'SHIFT':
                                self.keyboard_key(row, False, default=row, color=self.KEY_FUNC_COLOR)
                            elif row == '`' or row == '~':
                                self.keyboard_key(row, False)
                            else:
                                self.keyboard_key(row, True)

                    imgui.same_line()

                    imgui.push_style_color(imgui.COLOR_BUTTON, *self.KEY_FUNC_COLOR)
                    if imgui.button("BACKSPACE", width=135, height=60):
                        self.command = self.command[:-1]
                    imgui.pop_style_color(1)

                    imgui.push_style_color(imgui.COLOR_BUTTON, *self.KEY_FUNC_COLOR)
                    if imgui.button("SPACE", width=970, height=50):
                        self.command = self.command + " "
                    imgui.pop_style_color(1)

                    imgui.same_line()

                    imgui.push_style_color(imgui.COLOR_BUTTON, *self.KEY_FUNC_COLOR)
                    if imgui.button("ENTER", width=150, height=50):
                        self.command = self.command + "\n"
                    imgui.pop_style_color(1)

            except Exception as e:
                logging.error(e)
                self.CONSOLE_TEXT = str(e)
            imgui.end_group()

            # Command line
            imgui.text("Keyboard: {} | Shift: {} | SYS: {}".format(self.keyboard_toggled, self.CAPS, self.SYS))

            imgui.begin_child(
                "Child 2", height=70, width=-500, border=True,
                flags=imgui.WINDOW_ALWAYS_VERTICAL_SCROLLBAR
            )
            command = self.command
            imgui.text(command)
            imgui.end_child()



            # Buttons
            imgui.same_line()

            imgui.push_style_color(imgui.COLOR_BUTTON, *self.KEY_COLOR)
            if imgui.button("Confirm", width=200, height=60):
                with stdoutIO() as s:
                    try:
                        exec(command)
                    except Exception as e:
                        self.CONSOLE_TEXT = e
                self.CONSOLE_TEXT = s.getvalue()
            imgui.pop_style_color(1)

            imgui.same_line()

            imgui.push_style_color(imgui.COLOR_BUTTON, *self.KEY_COLOR)
            if imgui.button("Keyboard", width=200, height=60):
                if self.keyboard_toggled:
                    self.keyboard_toggled = False
                else:
                    self.keyboard_toggled = True
            imgui.pop_style_color(1)

            imgui.text('You wrote:')
            imgui.same_line()
            imgui.text(command)

            imgui.end()
            imgui.render()
            self.renderer.render()

        self.renderer.shutdown()
