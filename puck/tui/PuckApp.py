import asyncio

import urwid
import urwid.raw_display
from additional_urwid_widgets import DatePicker, MessageDialog

from puck.Games import FullGame, get_game_ids
from puck.utils import batch_request_create, batch_request_update


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
        self.games = asyncio.run(batch_request_create(_ids, 'banner'))

        # sizing
        self.screen = urwid.raw_display.Screen()
        (self.cols, self.rows) = self.screen.get_cols_rows()
        self._sizing()

        # top bar and header
        self.header = create_header()
        (self.game_panel, self.hidden_next) = create_game_panel(
            self, self.tb_rows
        )
        self.hidden_prev = []
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
        asyncio.run(batch_request_update(self.games))

    def switch_context(self, btn):
        # originally implemented using widgetPlaceholder however,
        # the listbox would not update resulting in context menu being
        # unselectable. Re-Render a whole new main display to work around
        self.context_menu = create_context_menu(
            self, btn.label, self.main_rows
        )
        self._reload_maindisplay()

    def cycle_games(self, btn):
        # when popping and pushing elements onto the widget lists and hidden lists,
        # care must be taken to not pop buttons or insert before/after buttons
        wl = self.game_panel.base_widget.widget_list

        if self.size < self.max_games:
            return

        if btn.label == 'Prev':
            if self.hidden_prev:
                rem = wl.pop(self.size - 1)
                new = self.hidden_prev.pop()
                self.hidden_next.insert(1, rem)
                wl.insert(1, new)

            else:
                pass
        else:
            if self.hidden_next:
                rem = wl.pop(1)
                new = self.hidden_next.pop(0)
                self.hidden_prev.append(rem)
                wl.insert(self.size - 1, new)
            else:
                pass

    def date_picker(self, btn):
        def destroy(btn):
            self.loop.widget = self.frame

        def change_date(btn):
            pass

        date_pick = DatePicker(
            highlight_prop=("dp_focus", "dp_no_focus")
        )
        cancel = urwid.Button('Cancel', on_press=destroy)
        select = urwid.Button('Select', on_press=change_date)
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

    def _reload_maindisplay(self):
        self.main_display = urwid.Columns(
            [
                ('weight', 1, self.context_menu),
                ('weight', 4, self.display)
            ], dividechars=1
        )
        self.list_walk[1] = self.main_display
        self.list_walk.set_focus(1)


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
    date_btn = urwid.Button(u'Date', on_press=app.date_picker)

    cards = [urwid.GridFlow([prev_btn], 8, 1, 1, 'center')]
    fill = False
    games = []

    if app.size > app.max_games:
        count = app.max_games
    elif app.size == 0:
        count = 0
        fill = True
    else:
        count = app.size
        fill = True
    ##################
    # if True:
    # #     count = app.max_games
    # #     fill = False
    # # elif False:
    # #     count = 0
    # #     fill = True
    # # else:
    # #     count = app.size
    # #     fill = True
########################
    for game in app.games:
        games.append(create_game_card(game, rows))
###########################
#     for game in range(5):
#         games.append(create_game_card(game, rows))
# ###########################
    for i in range(count):
        cards.append(('weight', 3, games[i]))
        if fill:
            cards.append(empty_card())

    cards.append(urwid.GridFlow([next_btn, date_btn], 8, 1, 1, 'center'))
    columns = urwid.Columns(cards)
    box = urwid.BoxAdapter(urwid.Filler(columns), rows)

    return (urwid.LineBox(box), games[count:])


# def create_game_card(i, rows):
#     home = urwid.Pile(
#         [
#             urwid.Text(u'NYR', align='center'),
#             urwid.Text(u'14', align='center')
#         ]
#     )

#     away = urwid.Pile(
#         [
#             urwid.Text(u'WSH', align='center'),
#             urwid.Text(u'1', align='center')
#         ]
#     )

#     if i == 0:
#         time = urwid.Text(u'07:30 PM EST', align='center')
#     elif i == 1 or i == 2:
#         if i == 1:
#             time = urwid.Text(u'2nd Int', align='center')
#         else:
#             time = urwid.Pile(
#                 [
#                     urwid.Text(u'01:37', align='center'),
#                     urwid.Text('1st', align='center')
#                 ]
#             )
#     else:
#         if i == 3:
#             time = urwid.Text(u'Final OT', align='center')
#         else:
#             time = urwid.Text(u'Final', align='center')

#     col = urwid.Columns([away, time, home], dividechars=1)

#     if rows > 2:
#         box = urwid.BoxAdapter(urwid.Filler(col), rows - 6)
#     else:
#         box = urwid.BoxAdapter(urwid.Filler(col), rows)

#     return urwid.LineBox(box)


def create_game_card(game, rows):
    home = urwid.Pile(
        [
            urwid.Text(game.home.abbreviation, align='center'),
            urwid.Text(str(game.home.goals), align='center')
        ]
    )

    away = urwid.Pile(
        [
            urwid.Text(game.away.abbreviation, align='center'),
            urwid.Text(str(game.away.goals), align='center')
        ]
    )

    if game.is_preview:
        time = urwid.Text(game.start_time, align='center')
    elif game.is_live:
        if game.in_intermission:
            time = urwid.Text(game.time + ' ' + game.period, align='center')
        else:
            time = urwid.Pile(
                [
                    urwid.Text(game.time, align='center'),
                    urwid.Text(game.period, align='center')
                ]
            )
    else:
        if game.period == 'OT':
            time = urwid.Text(u'Final OT', align='center')
        else:
            time = urwid.Text(u'Final', align='center')

    column = urwid.Columns([away, time, home], dividechars=1)

    if rows > 2:
        box = urwid.BoxAdapter(urwid.Filler(column), rows - 2)
    else:
        box = urwid.BoxAdapter(urwid.Filler(column), rows)

    return urwid.LineBox(column)


def empty_card():
    return urwid.Text('')


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
        Visit https://github.com/drsooch/puck for more information.'.format(VERSION)
    text = urwid.Text(start_text, align='center')
    box = urwid.BoxAdapter(urwid.Filler(text), rows)

    return urwid.LineBox(box)
