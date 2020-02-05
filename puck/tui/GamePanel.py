import urwid
import asyncio
import arrow
from copy import copy
from additional_urwid_widgets import DatePicker, MessageDialog
from puck.utils import batch_request_create, batch_request_update
from puck.Games import get_game_ids
from puck.tui.tui_utils import gametime_text_widget, box_wrap


class GamePanel(urwid.WidgetWrap):
    def __init__(self, app, rows):
        self.app = app
        self._rows = rows
        widget = self._create_game_panel()
        super().__init__(widget)

    def _update_in_place(self, date):
        self._w = self._create_game_panel(date)

    def _cycle_games(self, btn):
        # when popping and pushing elements onto the widget and  hidden lists,
        # care must be taken to not pop buttons or insert before/after buttons
        wl = self._w.base_widget.contents[2][0].widget_list

        if self.app.size < self.app.max_games:
            return

        if btn.label == 'Prev':
            if self.app.hidden_prev:
                rem = copy(wl[self.app.max_games - 1])
                new = self.app.hidden_prev.pop()
                self.app.hidden_next.append(rem)
                wl.insert(0, new)
                wl.remove(wl[self.app.max_games])
            else:
                pass
        else:
            if self.app.hidden_next:
                rem = copy(wl[0])
                new = self.app.hidden_next.pop()
                self.app.hidden_prev.append(rem)
                wl.append(new)
                wl.remove(wl[0])
            else:
                pass

    def _create_game_panel(self, date=None):
        next_btn = urwid.Button(u'Next', on_press=self._cycle_games)
        prev_btn = urwid.Button(u'Prev', on_press=self._cycle_games)
        date_btn = urwid.Button(
            u'Date', on_press=self.app._date_picker, user_data='panel'
        )

        if not date:
            _today = arrow.now().to('local').strftime('%a %b %d, %Y')
            date_text = urwid.Text(_today)
        else:
            date = date.get_date().strftime('%a %b %d, %Y')
            date_text = urwid.Text(date)

        num_games = urwid.Text(f'Game(s): {self.app.size}')

        btn_grid = urwid.GridFlow(
            [prev_btn, next_btn, date_btn], 8, 3, 1, 'center'
        )
        top_grid = urwid.GridFlow(
            [date_text, num_games, btn_grid], 30, 3, 1, 'center'
        )

        cards = []

        if self.app.size > self.app.max_games:
            count = self.app.max_games
        elif self.app.size == 0:
            count = 0
            cards = [
                ('weight', 2, self._empty_card()),
                urwid.Text(u'No games today. Select another date from above.'),
                ('weight', 2, self._empty_card())
            ]
        else:
            count = self.app.size

        for game in self.app.banner_games:
            self.app.hidden_next.appendleft(self._create_game_card(game))

        for i in range(count):
            cards.append(('weight', 3, self.app.hidden_next.pop()))

        columns = urwid.Columns(cards)
        pile = urwid.Pile([top_grid, urwid.Divider(), columns])

        box = box_wrap(pile, self._rows)

        return urwid.LineBox(box)

    def _create_game_card(self, game):
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

        time = gametime_text_widget(game)

        column = urwid.Columns([away, time, home], dividechars=1)

        if self._rows > 5:
            box = box_wrap(column, self._rows - 5)
        else:
            box = box_wrap(column, self._rows)

        return urwid.LineBox(box)

        def _empty_card(self):
            return urwid.Text('')
