import npyscreen as nps
import curses
from textwrap import wrap
from tui.MenuWidget import MenuBox
from tui.GameWidget import GameBox

DOCS_URL = 'https://github.com/drsooch/puck'
MAIN_TEXT = f'Welcome to Puck. Select an option from the Menu to begin. Check the Documentation here: {DOCS_URL}'


class MainForm(nps.FormBaseNew):
    def create(self):
        y, x = self.useable_space()
        self.menuBox = self.add(
            MenuBox, max_width=x // 5
        )
        self.gameBox = self.add(
            GameBox, max_height=y // 5, relx=(x // 5) + 2, rely=2, name='Games'
        )
        self.mainBox = self.add(
            MainBox, rely=(y // 5) + 2, relx=(x // 5) + 2, max_width=x * (4//5)
        )
        self.mainBox.create()

        handles = {
            curses.ascii.ESC: self.exit_func,
            '^Q': self.exit_func,
        }

        self.add_handlers(handles)

    def exit_func(self, _):
        exit(0)


class MainBox(nps.BoxTitle):
    _contained_widget = nps.MultiLine

    def create(self):
        self.values = wrap(MAIN_TEXT, self.width)
