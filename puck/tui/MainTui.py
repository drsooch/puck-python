import npyscreen as nps
from tui.MenuTui import MenuBox


class PuckApp(nps.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', MainWindow, name='Puck')


class MainWindow(nps.FormBaseNew):

    def create(self):
        y, x = self.useable_space()
        self.menuBox = self.add(MenuBox, max_width=x // 5)
        self.gameBox = self.add(GameBox, name='Games',
                                max_height=y // 5, relx=(x // 5) + 2, rely=2)
        self.mainBox = self.add(MainBox, rely=(y // 5) + 2, relx=(x // 5) + 2)


class GameBox(nps.BoxTitle):
    def create(self):
        pass


class MainBox(nps.BoxTitle):
    def create(self):
        pass


if __name__ == "__main__":
    puck = PuckApp().run()
