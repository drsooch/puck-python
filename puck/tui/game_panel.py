import asyncio
from copy import copy

import arrow
import urwid
from additional_urwid_widgets import DatePicker, MessageDialog

from puck.games import get_game_ids
from puck.tui.tui_utils import SelectableText, box_wrap, gametime_text_widget, Text
from puck.utils import batch_game_create, batch_game_update


class GamePanel(urwid.WidgetWrap):
    def __init__(self, app, rows):
        self.app = app
        self._rows = rows
        widget = self._create_game_panel()
        super().__init__(widget)

# -------------------------- Top Level Methods --------------------------#
    def _update_in_place(self, date):
        self._w = self._create_game_panel(date)
        self.app._reload_topbar()

# -------------------------- Button Methods --------------------------#
    def cycle_games(self, btn, data=None):
        # when popping and pushing elements onto the widget and  hidden lists,
        # care must be taken to not pop buttons or insert before/after buttons

        # depending on the size of the terminal, may have an extra widget
        if self.app.sizing.gp_divider:
            index = 2
        else:
            index = 1

        wl = self._w.base_widget.contents[index][0].widget_list

        if self.app.size < self.app.max_games:
            return

        if btn.label == 'Prev':
            if self.app.hidden_prev:
                # copy the last game that will be popped off
                rem = copy(wl[self.app.max_games - 1])
                # pop off the new game from the hidden queue
                new = self.app.hidden_prev.pop()
                # add the removed game to the hidden queue
                self.app.hidden_next.append(rem)
                # put the new game in front
                wl.insert(0, new)
                # remove the final game (which is now at index max games)
                wl.remove(wl[self.app.max_games])
            else:
                pass
        else:
            if self.app.hidden_next:
                # copy first game
                rem = copy(wl[0])
                # pop off the new game from hidden queue
                new = self.app.hidden_next.pop()
                # add removed node to first queue
                self.app.hidden_prev.append(rem)
                # push the new game onto panel
                wl.append(new)
                # remove first game
                wl.remove(wl[0])
            else:
                pass

    def change_date(self, btn):
        def destroy():
            # removes pop-up
            self.app.loop.widget = self.app.frame

        # get the ids for given day
        _ids = get_game_ids(params={'date': str(btn.data.get_date())})
        self.app.banner_games = asyncio.run(
            batch_game_create(_ids, 'banner', self.app.db_conn)
        )

        self.app.size = len(self.app.banner_games)
        # populates deques
        self.app._populate_hidden()
        self._update_in_place(btn.data)
        destroy()

    def date_picker(self, btn):
        self.app._date_picker(btn, self)

# -------------------------- Helper Methods --------------------------#
    def _create_game_panel(self, date=None) -> urwid.LineBox:
        next_btn = SelectableText(u'Next', on_press=self.cycle_games)
        prev_btn = SelectableText(u'Prev', on_press=self.cycle_games)
        date_btn = SelectableText(
            u'Date', on_press=self.date_picker, user_data=self
        )

        if not date:
            date = arrow.now().to('local')
        else:
            date = date.get_date()

        if self.app.sizing.gp_main > 20:
            date_text = urwid.Text(date.strftime('%a %b %d, %Y'))
        else:
            date_text = urwid.Text(date.strftime('%x'))

        num_games = urwid.Text(f'Game(s): {self.app.size}')

        btn_grid = urwid.GridFlow(
            [prev_btn, next_btn, date_btn],
            self.app.sizing.gp_btns, 3, 1, 'center'
        )

        if self.app.sizing.gp_main < 16:
            top_grid = urwid.GridFlow(
                [date_text, num_games, prev_btn, next_btn, date_btn],
                self.app.sizing.gp_main, 2, 1, 'center'
            )
        else:
            top_grid = urwid.GridFlow(
                [date_text, num_games, btn_grid],
                self.app.sizing.gp_main, 3, 1, 'center'
            )

        cards = []

        if self.app.size > self.app.max_games:
            count = self.app.max_games
        elif self.app.size == 0:
            count = 0
            cards = [
                Text(u'No games today. Select another date from above.'),
            ]
        else:
            count = self.app.size

        for game in self.app.banner_games:
            self.app.hidden_next.appendleft(self._create_game_card(game))

        for i in range(count):
            cards.append(('weight', 3, self.app.hidden_next.pop()))

        columns = urwid.Columns(cards)

        if self.app.sizing.gp_divider:
            pile = urwid.Pile([top_grid, urwid.Divider(), columns])
        else:
            pile = urwid.Pile([top_grid, columns])

        box = box_wrap(pile, self._rows)

        return urwid.LineBox(box)

    def _create_game_card(self, game) -> urwid.LineBox:
        home = urwid.Pile(
            [
                Text(game.home.abbreviation),
                Text(str(game.home.goals))
            ]
        )

        away = urwid.Pile(
            [
                Text(game.away.abbreviation),
                Text(str(game.away.goals))
            ]
        )

        time = gametime_text_widget(game)

        column = urwid.Columns([away, time, home], dividechars=1)

        if self._rows > 5:
            box = box_wrap(column, self._rows - 5)
        else:
            box = box_wrap(column, self._rows)

        return urwid.LineBox(box)

    def _empty_card(self) -> urwid.Text:
        return urwid.Text('')
