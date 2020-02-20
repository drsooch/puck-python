import asyncio
from collections import defaultdict
from copy import deepcopy

import arrow
import urwid
from additional_urwid_widgets import IndicativeListBox

from puck.games import get_game_ids, BaseGame
from puck.tui.tui_utils import (
    BaseContext, BaseDisplay, HButton, box_wrap,
    gametime_text_widget, long_strf, SelectableText
)
from puck.utils import batch_request_create, batch_request_update

BOX_STATS = [
    ('SOG', 'periods'),
    ('PPG', 'powerPlayGoals'),
    ('PPA', 'powerPlayOpportunities'),
    ('PP%', 'powerPlayPercentage'),
    ('PIMS', 'pim'),
    ('Hits', 'hits'),
    ('FOW%', 'faceOffWinPercentage')
]


class GamesContext(BaseContext):
    """Controls the Game Submenu Context."""

    def __init__(self, app, rows):
        BaseContext.__init__(self, app, rows)

        # create the context's menu and opening display
        self.menu = self.context_menu()
        self.display = GameDisplay(self.app, self, self._rows)

    def context_menu(self):
        choices = [u'Today', u'Select Date', u'Select Game', u'Schedule']
        btns = []
        for c in choices:
            btns.append(HButton(c, on_press=self.switch_display))

        btn_grid = urwid.GridFlow(btns, 15, 10, 1, 'center')
        box = box_wrap(btn_grid, self._rows)

        return urwid.LineBox(box, 'Games Menu')

    def switch_display(self, btn, data=None):
        """Handle all menu options.
        Some options are not applicable to the Context's current display."""

        if btn.label == 'Today':
            # check to see if display is correct
            if type(self.display) is GameDisplay:
                self.display.today()
            else:
                self.display = GameDisplay(self.app, self, self._rows)
        elif btn.label == 'Select Date':
            self.app._date_picker(btn=btn, caller=self)
        # elif btn.label == 'Select Game' or isinstance(data, BaseGame):
        # self.display = SingleGameDisplay(self.app, self, self._rows, data)
        elif btn.label == 'Schedule':
            self.display = ScheduleDisplay(self.app, self, self._rows)
        else:
            self.app.error_message(
                f'Something horrible went wrong or that function is not \
                implemented', (50, 6)
            )

        # must be called to tell the screen to update
        self.app._reload_maindisplay()

    def change_date(self, btn, date):
        # this function should only be called with GameDisplay
        # Possible force an early return
        # if the current display is not a GameDisplay
        if type(self.display) is not GameDisplay:
            self.display = GameDisplay(self.app, self, self._rows)

        # Read: GameDisplay.change_date()
        self.display.change_date(btn, date)

        self.app._reload_maindisplay()

    def update(self):
        self.display.update()


class GameDisplay(urwid.WidgetWrap, BaseDisplay):
    """Widget Handler for displaying the box scores for a dates games.
    Used in the GamesContext.
    """

    def __init__(self, app, ctx, rows):
        BaseDisplay.__init__(self, app, ctx, rows)
        _ids = get_game_ids()
        # number of games
        self.size = len(_ids)

        # list of game objects
        self.full_games = asyncio.run(batch_request_create(_ids, 'full'))

        # date of games on display
        self.display_date = arrow.now().date()

        widget = self.main_display()

        # holds reference to today's games in case date is swapped
        self.todays_games = deepcopy(self.full_games)

        urwid.WidgetWrap.__init__(self, widget)

# -------------------------- Top Level Methods --------------------------#
    def update(self):
        """Update all data encompassed by object."""
        # TODO: create logic to remove updating both unneccessarily
        asyncio.run(batch_request_update(self.full_games))
        asyncio.run(batch_request_update(self.todays_games))

    def _update_in_place(self):
        # this method is purely for readability
        self._w = self.main_display()

# -------------------------- Button Methods --------------------------#
    def today(self):
        """show today's box scores"""
        if self.display_date == arrow.now().date():
            # already on today's games
            return
        else:
            self.display_date = arrow.now().date()

        self.full_games = self.todays_games  # no need to deepcopy
        self.size = len(self.full_games)
        self._update_in_place()

    def change_date(self, btn, date):
        """Change the box score display to the provided date."""
        date = date.get_date()

        if date == self.display_date:
            self.app.destroy()
            return
        else:
            self.display_date = date

        _ids = get_game_ids(params={'date': str(date)})
        self.size = len(_ids)
        self.full_games = asyncio.run(batch_request_create(_ids, 'full'))

        self._update_in_place()
        self.app.destroy()

# -------------------------- Helper Methods --------------------------#
    def _create_game_card(self, game):
        title = SelectableText(
            game.away.long_name + ' at ' + game.home.long_name,
            on_press=self.ctx.switch_display,
            user_data=game
        )

        home = urwid.Pile(
            [
                urwid.Text(game.home.abbreviation, align='center'),
                urwid.Text(str(game.home['goals']), align='center')
            ]
        )

        away = urwid.Pile(
            [
                urwid.Text(game.away.abbreviation, align='center'),
                urwid.Text(str(game.away['goals']), align='center')
            ]
        )

        time = gametime_text_widget(game)

        game_card = urwid.Columns([away, time, home])
        game_card = urwid.LineBox(game_card)

        box_score = [
            urwid.Pile(
                [
                    urwid.Text(u'Team', 'center'),
                    urwid.Text(game.home.abbreviation, 'center'),
                    urwid.Text(game.away.abbreviation, 'center')
                ]
            )
        ]
        for stat in BOX_STATS:
            # hard code this path b/c it requires one more step of indirection
            if stat[1] == 'periods':
                val_h = game.home.periods.total_shots
                val_a = game.away.periods.total_shots
            else:
                val_h = game.home[stat[1]]
                val_a = game.away[stat[1]]

            if stat[0] in ['FOW%', 'PP%']:
                val_h += '%'
                val_a += '%'

            # when read from JSON, these values operate as floats not ints
            if stat[0] in ['PPG', 'PPA']:
                val_h = int(val_h)
                val_a = int(val_a)

            pile = urwid.Pile(
                [
                    urwid.Text(stat[0], 'center'),
                    urwid.Text(str(val_h), 'center'),
                    urwid.Text(str(val_a), 'center')
                ]
            )

            box_score.append(pile)

        box_score_col = urwid.GridFlow(box_score, 6, 2, 1, 'center')
        full_card = urwid.Pile([title, game_card, box_score_col])

        return urwid.LineBox(full_card)

    def main_display(self):
        """Main logic for building the box scores for GamesDisplay"""
        # TODO: Clean up logic for column creation
        date = self.display_date.strftime('%A %B %d, %Y')
        date_text = urwid.Text(
            date + ' | Game(s): ' + str(self.size), align='center'
        )

        cards = [urwid.Divider('-'), date_text, urwid.Divider('-')]
        # put game box scores side by side
        for i, game in enumerate(self.full_games):
            if i % 2 == 0:  # when even its the "first" column
                prev = self._create_game_card(game)
            else:  # else it needs to be paired with the prev column
                curr = self._create_game_card(game)
                col = urwid.Columns([prev, curr], dividechars=1)
                cards.append(col)

        # if there is an extra game box score add it last
        if self.size % 2 != 0:
            cards.append(urwid.Columns([prev]))

        lw = urwid.SimpleFocusListWalker(cards)
        idlb = IndicativeListBox(lw)
        box = urwid.BoxAdapter(idlb, self._rows)

        return urwid.LineBox(box)


class ScheduleDisplay(urwid.WidgetWrap, BaseDisplay):
    """Handles the display of a weekly Schedule for GamesContext"""

    def __init__(self, app, ctx, rows):
        BaseDisplay.__init__(self, app, ctx, rows)
        today = arrow.now()
        shift = today.isoweekday() - 1

        # Week starts on a monday when isoweekday = 1
        self.current_week_start = today.shift(days=-shift)
        self.current_week_end = self.current_week_start.shift(days=+6)

        self.prev_btn = HButton('Prev', on_press=self.previous_page)
        self.next_btn = HButton('Next', on_press=self.next_page)

        # holds BaseGame objects for each day in the current week
        self.current_week_games = defaultdict(lambda: [])

        # populate the current_weeks_games
        self._request_games()
        widget = self.build_schedule()

        urwid.WidgetWrap.__init__(self, widget)

    def update(self):
        pass
# -------------------------- Button Methods --------------------------#

    def previous_page(self, btn):
        """cycle to the previous week"""
        self.current_week_start = self.current_week_start.shift(days=-7)
        self.current_week_end = self.current_week_end.shift(days=-7)

        self._request_games()

        self._w = self.build_schedule()

    def next_page(self, btn):
        """cycle to the next week"""
        self.current_week_start = self.current_week_start.shift(days=+7)
        self.current_week_end = self.current_week_end.shift(days=+7)

        self._request_games()

        self._w = self.build_schedule()

# -------------------------- Helper Methods --------------------------#
    def build_schedule(self):
        """Main logic for building the schedule widget."""
        title = urwid.Text(
            'Week of {} to {}'.format(
                long_strf(self.current_week_start),
                long_strf(self.current_week_end)
            ), 'center'
        )
        widgets = [urwid.Divider('-'), title, urwid.Divider('-')]

        for day, games in self.current_week_games.items():
            widgets.append(urwid.Text(str(long_strf(day)), 'center'))
            widgets.append(urwid.Divider('-'))
            for game in games:
                teams = urwid.Text(
                    game.away.long_name + ' at ' + game.home.long_name,
                    align='center'
                )
                if game.is_live or game.is_final:
                    game_status = urwid.Text(
                        str(game.away['goals']) + ' - ' + str(game.home['goals']),  # noqa
                        align='center'
                    )
                else:
                    game_status = urwid.Text(
                        game.start_time, 'center'
                    )

                widgets.append(
                    urwid.Columns([teams, game_status])
                )
                widgets.append(urwid.Divider('-'))
            widgets.append(urwid.Divider())

        btn_grid = urwid.GridFlow(
            [self.prev_btn, self.next_btn], 10, 2, 1, 'center'
        )
        widgets.append(btn_grid)
        lw = urwid.SimpleFocusListWalker(widgets)
        idlb = IndicativeListBox(lw)

        box = urwid.BoxAdapter(idlb, self._rows)

        return urwid.LineBox(box)

    def _request_games(self):
        """Request the current weeks games."""
        # clear the dictionary to start fresh
        self.current_week_games.clear()

        start = self.current_week_start.date()
        end = self.current_week_end.date()

        # NOTE: a batch request for ALL dates is chosen because the speed
        # gain is much better than individual requesting each day of the week
        _ids = get_game_ids(
            params={
                'startDate': str(start),
                'endDate': str(end)
            }
        )

        games = asyncio.run(batch_request_create(_ids, 'banner'))

        # this partitions games by their date
        for game in games:
            self.current_week_games[game.game_date].append(game)


class SingleGameDisplay(urwid.WidgetWrap, BaseDisplay):
    """Displays a single games full stats."""

    def __init__(self, app, ctx, row, game):
        BaseDisplay.__init__(self, app, ctx, row)

        self.game = game

        widget = urwid.Text('Testing.')
        urwid.WidgetWrap.__init__(self, widget)

    def update(self):
        return super().update()
