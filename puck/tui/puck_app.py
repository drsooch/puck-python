import asyncio
from collections import deque
from copy import copy

import urwid
import urwid.raw_display
from additional_urwid_widgets import DatePicker, MessageDialog
from puck.games import get_game_ids
from puck.utils import batch_request_create, batch_request_update
from puck.tui.game_panel import GamePanel
from puck.tui.game_context import GamesContext

VERSION = '0.1'
ROW_SPACE = 6
APP_PROP = 4

PALETTE = [
    ('main', 'white', 'black'),
    ('menu_focus', 'standout', ''),
    ('dp_focus', 'black', 'white'),
    ('dp_no_focus', 'white', 'black'),
]


def exit_handler(btn=None):
    raise urwid.ExitMainLoop()


class PuckApp(object):
    def __init__(self):
        _ids = get_game_ids()
        self.size = len(_ids)
        self.banner_games = asyncio.run(batch_request_create(_ids, 'banner'))

        # sizing
        self.screen = urwid.raw_display.Screen()
        (self.cols, self.rows) = self.screen.get_cols_rows()
        self._sizing()

        # top bar and header
        self.header = create_header()
        self._populate_hidden()
        self.game_panel = GamePanel(self, self.tb_rows)

        self.main_menu = create_main_menu(self, self.tb_rows)

        self.top_bar = urwid.Columns(
            [
                ('weight', 1, self.main_menu),
                ('weight', 4, self.game_panel)
            ], dividechars=1,
        )

        # main display
        self.context = None
        self.context_menu = create_opening_menu(self.main_rows)
        self.display = create_opening_page(self.main_rows)
        self.main_display = urwid.Columns(
            [
                ('weight', 1, self.context_menu),
                ('weight', 4, self.display)
            ], dividechars=1
        )

        self.list_walk = urwid.SimpleFocusListWalker(
            [self.top_bar, self.main_display]
        )
        self.body = urwid.ListBox(self.list_walk)
        self.frame = urwid.Frame(
            urwid.AttrWrap(self.body, 'main'),
            header=urwid.AttrWrap(self.header, 'main')
        )

        self.loop = urwid.MainLoop(
            self.frame, palette=PALETTE, screen=self.screen, pop_ups=True
        )

    # -------------------------- Top Level Methods -------------------------#
    def run(self):
        self.loop.run()

    def update(self):
        asyncio.run(batch_request_update(self.banner_games))

    # -------------------------- Button Methods --------------------------#
    def destroy(self, btn=None):
        self.loop.widget = self.frame

    def error_message(self, msg, size=None):
        ok = urwid.Button(u'OK', on_press=self.destroy)
        if not size:
            size = (self.cols // 3, self.rows // 3)
        self.loop.widget = MessageDialog(
            [msg], [ok], size, background=self.frame, contents_align='center'
        )

    def switch_context(self, btn):
        # originally implemented using widgetPlaceholder however,
        # the listbox would not update resulting in context menu being
        # unselectable. Re-Render a whole new main display to work around
        self.context = GamesContext(self, self.main_rows)
        self.display = self.context.display
        self.context_menu = self.context.menu
        self._reload_maindisplay()

    def _date_picker(self, btn, caller):
        """
        Date Picker widget creater. Caller refers to which button is
        calling the method: the game panel or game display.
        """
        on_press = getattr(caller, 'change_date')

        date_pick = DatePicker(
            highlight_prop=("dp_focus", "dp_no_focus")
        )
        cancel = urwid.Button('Cancel', on_press=self.destroy)
        select = urwid.Button(
            'Select', on_press=on_press, user_data=date_pick
        )
        btn_grid = urwid.GridFlow([cancel, select], 10, 5, 1, 'center')

        base = urwid.Pile(
            [
                urwid.Text(u'Use ctrl + "arrow key" to change the date.'),
                date_pick,
                btn_grid
            ]
        )

        box = urwid.LineBox(base, title='Select a Date', title_align='center')

        fill = urwid.AttrMap(urwid.Filler(box), 'date_pick')

        overlay = urwid.Overlay(
            fill, self.frame, 'center',
            44, 'middle', 7           # HACK to get the pop up to fit properly.
        )

        self.loop.widget = overlay

# -------------------------- Helper Methods --------------------------#
    def _sizing(self):
        self.rows = self.rows - ROW_SPACE  # remove space for proper rendering
        self.tb_rows = self.rows // APP_PROP
        self.main_rows = self.rows - self.tb_rows

        if self.cols <= 80:
            self.max_games = 1
        elif self.cols <= 110:
            self.max_games = 2
        elif self.cols <= 135:
            self.max_games = 3
        elif self.cols <= 165:
            self.max_games = 4
        else:
            self.max_games = 5

    def _populate_hidden(self):
        self.hidden_prev = deque([], self.size)
        self.hidden_next = deque([], self.size)

    def _reload_maindisplay(self):
        # Have to "reset" the display variable to get the new context display
        self.display = self.context.display

        self.main_display = urwid.Columns(
            [
                ('weight', 1, self.context_menu),
                ('weight', 4, self.display)
            ], dividechars=1
        )
        self.list_walk[1] = self.main_display
        self.list_walk.set_focus(1)

    def _reload_topbar(self):
        self.top_bar = urwid.Columns(
            [
                ('weight', 1, self.main_menu),
                ('weight', 4, self.game_panel)
            ], dividechars=1,
        )

        self.list_walk[0] = self.top_bar
        self.list_walk.set_focus(0)


def create_header():
    return urwid.Text(u'Puck v{}'.format(VERSION), align='center')


def create_main_menu(app, rows):
    choices = [u'Standings', u'Games', u'Teams', u'Players']
    btns = []
    for c in choices:
        btns.append(urwid.Button(c, on_press=app.switch_context))

    btn_grid = urwid.GridFlow(btns, 15, 10, 1, 'center')

    box = urwid.BoxAdapter(urwid.Filler(btn_grid), rows)
    return urwid.LineBox(box, title='Main Menu')


def create_context_menu(app, context, rows):
    choices = [u'Standings', u'Games', u'Teams', u'Players']
    btns = []
    for c in choices:
        btns.append(urwid.Button(c, on_press=app.switch_context))

    btn_grid = urwid.GridFlow(btns, 15, 10, 1, 'center')
    box = urwid.BoxAdapter(urwid.Filler(btn_grid), rows)

    return urwid.LineBox(box, f'{context}')


def create_opening_menu(rows):
    text = urwid.Text(u'')
    box = urwid.BoxAdapter(urwid.Filler(text), rows)

    return urwid.LineBox(box)


def create_opening_page(rows):
    start_text = u'Welcome to Puck version: {}\n \
        Visit https://github.com/drsooch/puck for more information.'.format(VERSION)  # noqa
    text = urwid.Text(start_text, align='center')
    box = urwid.BoxAdapter(urwid.Filler(text), rows)

    return urwid.LineBox(box)