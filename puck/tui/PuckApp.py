import asyncio
from collections import deque
from copy import copy

import urwid
import urwid.raw_display
from additional_urwid_widgets import DatePicker, MessageDialog
from puck.Games import get_game_ids
from puck.utils import batch_request_create, batch_request_update
from puck.tui.GamePanel import GamePanel

VERSION = '0.1'
ROW_SPACE = 6
APP_PROP = 4

PALETTE = [
    ('main', 'white', 'black'),
    ('dp_focus', 'black', 'white'),
    ('dp_no_focus', 'white', 'black'),
    ('test', 'white', 'dark blue')
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

    def run(self):
        self.loop.run()

    def update(self):
        asyncio.run(batch_request_update(self.banner_games))

    def switch_context(self, btn):
        # originally implemented using widgetPlaceholder however,
        # the listbox would not update resulting in context menu being
        # unselectable. Re-Render a whole new main display to work around
        self.context_menu = create_context_menu(
            self, btn.label, self.main_rows
        )
        self._reload_maindisplay()

    def _date_picker(self, btn, caller):
        """
        Date Picker widget creater. Caller refers to which button is
        calling the method: the game panel or game display.
        """
        def destroy(btn=None):
            self.loop.widget = self.frame
        if caller == 'panel':
            def change_date(btn, date):
                _ids = get_game_ids(params={'date': str(date.get_date())})
                self.banner_games = asyncio.run(
                    batch_request_create(_ids, 'banner')
                )
                self.size = len(self.banner_games)
                self._populate_hidden()
                self.game_panel._update_in_place(date)
                self._reload_topbar()
                destroy()
        else:
            def change_date(btn, date):
                print('changed')

        date_pick = DatePicker(
            highlight_prop=("dp_focus", "dp_no_focus")
        )
        cancel = urwid.Button('Cancel', on_press=destroy)
        select = urwid.Button(
            'Select', on_press=change_date, user_data=date_pick
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

        fill = urwid.AttrMap(urwid.Filler(box), 'test')

        overlay = urwid.Overlay(
            fill, self.frame, 'center',
            44, 'middle', 7           # HACK to get the pop up to fit properly.
        )

        self.loop.widget = overlay

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
