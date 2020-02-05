import urwid
import asyncio
from puck.Games import get_game_ids
from puck.utils import batch_request_create, batch_request_update
from puck.tui.tui_utils import gametime_text_widget


class GameDisplay(object):
    def __init__(self):
        _ids = get_game_ids()
        self.full_games = asyncio.run(batch_request_create(_ids, 'full'))
        self.widget = None

    def main_display(self):
        cards = []
        for game in self.full_games:
            cards.append(self._create_game_card(game))
        pass

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
        
        return urwid.LineBox(None)

    def single_game_display(self):
        pass

    def schedule_display(self):
        pass
