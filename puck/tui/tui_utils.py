import urwid


def gametime_text_widget(game):
    """Helper function to generate the Game Time Text Widget"""
    if game.is_preview:
        time = urwid.Text(game.start_time, align='center')
    elif game.is_live:
        if game.in_intermission:
            time = urwid.Text(
                game.time + ' ' + game.period, align='center'
            )
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
        elif game.period == 'SO':
            time = urwid.Text(u'Final SO', align='center')
        else:
            time = urwid.Text(u'Final', align='center')

    return time


def box_wrap(widget, rows):
    """Helper function wrapping a widget in a Filler and then Box Adapter."""
    return urwid.BoxAdapter(
        urwid.Filler(widget), rows
    )
