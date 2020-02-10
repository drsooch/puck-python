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


def long_strf(date):
    return date.strftime('%A %B %d, %Y')


def short_strf(date):
    return date.strftime('%a %b %d, %Y')


class HButton(urwid.Button):
    """Gonna make this highlight the full cell. Eventually"""

    def __init__(self, label, on_press=None, user_data=None):
        super().__init__(label, on_press, user_data)


class SelectableText(urwid.WidgetWrap):
    """This widget is designed to emulate a button without the nasty < and >.

        On keypress ie. "Space" or "Enter" the widget will function like a
        regular button.
    """

    def __init__(self, text, on_press=None, user_data=None):
        """[summary]

        Args:
            text (str): string of text for display
            on_press (function, optional): a function for callback when enter
                                           or space is pressed.
            user_data (any, optional): any data that needs to be passed to the
                                       callback.
        """
        self.label = text
        self.text = urwid.Text(self.label, align='center')
        self.wrapped_text = urwid.AttrMap(self.text, None, 'menu_focus')
        self._listbox = urwid.ListBox([self.wrapped_text])
        self.callback = on_press
        self.data = user_data
        widget = urwid.BoxAdapter(self._listbox, 1)
        super().__init__(widget)

    def keypress(self, size, key):
        if self.callback is None:
            return key

        if key == " ":
            self.callback(self, self.data)
        if key == "enter":
            self.callback(self, self.data)

        return key


class BaseContext(object):
    """Base class for a Context. Should not be instantiated directly.
    Child class should implement an update, context_menu,
    and switch_context methods.
    """

    def __init__(self, app, rows):
        self.app = app
        self._rows = rows
        self.menu = None
        self.display = None

        super().__init__()

    def update(self):
        raise NotImplementedError('Implement an update method for the context')

    def context_menu(self):
        raise NotImplementedError(
            'Implement a context_menu method for the context'
        )

    def switch_context(self):
        raise NotImplementedError(
            'Implement a switch_context method for the context'
        )

    def __repr__(self):
        return f'{self.__class__} -> {self.__dict__}'


class BaseDisplay(object):
    def __init__(self, app, ctx, rows):
        # main app
        self.app = app

        # context the display lives in
        self.ctx = ctx

        # rows of widget
        self._rows = rows

        super().__init__()

    def update(self):
        raise NotImplementedError('Implement an update method for the display')
