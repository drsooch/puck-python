import npyscreen as nps

MENU_VALUES = [
    'Teams',
    'Players',
    'Standings',
    'Games'
]


class MenuMultiLineAction(nps.MultiLineAction):
    def create(self):
        pass


class MenuBox(nps.BoxTitle):
    _contained_widget = MenuMultiLineAction

    def __init__(self, screen, *args, **keywords):
        super().__init__(screen, name='Menu', values=MENU_VALUES, *args, **keywords)
