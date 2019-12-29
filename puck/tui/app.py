import npyscreen as nps

from tui.MainForm import MainForm


class PuckApp(nps.NPSAppManaged):
    def onStart(self):
        self.MainForm = self.addForm('MAIN', MainForm, name='Puck')
