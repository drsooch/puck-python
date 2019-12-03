import npyscreen as nps

MENU_VALUES = [
    'Teams',
    'Players',
    'Standings',
    'Games'
]


class MenuBox(nps.BoxTitle):
    _contained_widget = nps.MultiLineAction

    def actionHighlighted(self):
        print(self)

    def create(self):
        self.name = 'Menu'
        self.values = MENU_VALUES
