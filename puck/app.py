import sys

import urwid
import urwid.raw_display

from puck.tui.puck_app import PuckApp
# TUI entry point


def main():
    app = None
    try:
        app = PuckApp()
        app.run()
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
    except Exception as err:
        print(str(err))
    finally:
        if app:
            app.db_conn.close()

    sys.exit(0)
