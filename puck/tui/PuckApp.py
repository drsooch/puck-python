from puck.Games import FullGame, get_game_ids
from puck.utils import batch_request_create, batch_request_update
import asyncio
import urwid
import urwid.raw_display

VERSION = '0.1'


def exit_handler(btn=None):
    raise urwid.ExitMainLoop()


class PuckApp(object):
    def __init__(self):
        _ids = get_game_ids()
        self.size = len(_ids) - 1
        self.games = asyncio.run(batch_request_create(_ids, 'banner'))

        # sizing
        self.screen = urwid.raw_display.Screen()
        (self.cols, self.rows) = self.screen.get_cols_rows()
        self.rows = self.rows - 6  # remove space for proper rendering
        self.tb_rows = self.rows // 4
        self.main_rows = self.rows - self.tb_rows

        self.header = create_header()
        self.game_panel = create_game_panel(self, self.tb_rows)
        self.main_menu = create_main_menu(self, self.tb_rows)

        self.top_bar = urwid.Columns(
            [
                ('weight', 1, self.main_menu),
                ('weight', 4, self.game_panel)
            ], dividechars=1,
        )

        self.context_menu = urwid.WidgetPlaceholder(
            create_opening_menu(self.main_rows))
        self.display = urwid.WidgetPlaceholder(
            create_opening_page(self.main_rows))
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
        self.frame = urwid.Frame(self.body, header=self.header)

    def run(self):
        urwid.MainLoop(
            self.frame, screen=self.screen,  # unhandled_input=exit_handler
        ).run()

    def update(self):
        asyncio.run(batch_request_update(self.games))

    def switch_context(self, btn):
        print(f'Switching context: {btn.label}')
        self.context_menu.original_widget = create_context_menu(
            self, btn.label, self.main_rows
        )

    def cycle_games(self, btn):
        print(f'Cycling: {btn.label}')


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


def create_game_panel(app, rows):
    next_btn = urwid.Button(u'Next', on_press=app.cycle_games)
    prev_btn = urwid.Button(u'Prev', on_press=app.cycle_games)

    cards = [urwid.GridFlow([prev_btn], 8, 1, 1, 'center')]
    # for game in self.games:
    for i in range(5):
        cards.append(urwid.Text(u'Testing'))

    cards.append(urwid.GridFlow([next_btn], 8, 1, 1, 'center'))

    columns = urwid.Columns(cards)
    box = urwid.BoxAdapter(urwid.Filler(columns), rows)
    return urwid.LineBox(box)


def create_context_menu(app, context, rows):
    choices = [u'Standings', u'Games', u'Teams', u'Players']
    btns = []
    for c in choices:
        btns.append(urwid.Button(c, on_press=app.switch_context))

    btn_grid = urwid.GridFlow(btns, 15, 10, 1, 'center')
    box = urwid.BoxAdapter(urwid.Filler(btn_grid), rows)

    return urwid.LineBox(box, 'Context Menu')


def create_opening_menu(rows):
    text = urwid.Text(u'')
    box = urwid.BoxAdapter(urwid.Filler(text), rows)

    return urwid.LineBox(box)


def create_opening_page(rows):
    start_text = u'Welcome to Puck version: {}\n \
        Visit https://github.com/drsooch/puck for more information.'.format(VERSION)
    text = urwid.Text(start_text, align='center')
    box = urwid.BoxAdapter(urwid.Filler(text), rows)

    return urwid.LineBox(box)
