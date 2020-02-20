# Puck
Puck the NHL CLI and TUI.
***
# Current Status:
Version 0.1 is being pushed to the repository. (Quite an arbitrary version number I know.)
Part of the reasoning behind this is to expose my code to the outside world.
Features are slowly being evolved, unfortunately a new semester has started and I have to
stay on top of my impending workload.

## CLI:
The CLI interface is barebones. Currently only one subcommand is implemented: games.

![puck cli](imgs/PuckCLIusage.png)

The main options are also not workable (-v and -o). I decided to make a TUI before I could
iterate further on the CLI.

Using the games subcommand is straightforward:

![game command](imgs/PuckCLIgames.png)

Selecting the option simply prints out the selected time frames games.

![game command in action](imgs/PuckCLIgamesquery.png)

> **NOTE:** While writing this README, I realized I didn't fully implement the date range command.
> It will print out all the games with no delineation between them. **WOO!**


## TUI
The actual TUI has its framework pretty set in stone. Unfortunately, I struggled with
wrangling Urwid framework to conform to the Terminals size. In its current state a lot of
sizing is hardcoded to fit in a full-screen terminal. Please let me know if you run into any
issues with sizing let me know! (all 2 of you reading this)

![Puck TUI usage](imgs/PuckTUImain.png)

The Games menu option is currently the only one available. You can drill down into the box scores for past games and look at the
upcoming schedule. Single Game Display is up next, but first work needs to be on tracking player stats for a more
fleshed out experience.
There's not much else you can do besides look at today's games. You can use the date selector to take a peek at other days.
As mentioned previously, sizing is off so in instances where there are not many games the sizing will look absurd...

![showing off the date button](imgs/PuckTUIdate.png)

![Schedule View](imgs/PuckTUIschedule.png)

![Box Scores](imgs/PuckTUIboxscore.png)

The TUI now uses an SQLite3 database internally. In order to track players attempting to query a full teams roster
would take exceptionally long. The database also removes any issues if a connection error was undergone when querying these players.

**Note:** Yes the color of the date box is gross. It's for testing purposes :).

## Install and Run

If for whatever reason you actually want to take the time to download and use this thing. Clone this repo.

`git clone https://github.com/drsooch/puck.git`

Create a Python virtual environment (3.7>)

`python3 -m venv venv_dir`

Place the source files in under a directory in `venv_dir` whatever that may be.

Install any required modules.

`pip3 install -r requirements.txt`

The config file must be updated to point to the correct location. There is no setup.py script yet, so this must be done
manually. I currently have `$PYTHONPATH` set in my environment to point to the root `venv_dir` folder.
You can keep the config file as-is but you must set your `$PYTHONPATH` to point to the correct location.

Finally, run it.

`python3 puck/__main__.py`

On first setup the beginning database files and tables will be created. Please note, there is no excess logic to catch any database or connection issues
so this may take a few attempts. (It usually fails on poor connection to the internet.)

The `__main__.py` file will be the eventual executable. It currently only
opens the TUI app, change the `if True:` to `False` to get the CLI

Wait what's that? Python failed to import puck.whatever?
This happened more times than I can count. My best answer, until I clean up the code,
is to play with the import paths until one works.

## Final Notes:

If you see code that "smells" or could be implemented differently, please don't hesitate to let me know.
I'm always open to suggestions and critiques!

The code has a mix of docstrings and no docstrings. I haven't found the time to go through and create docstrings
for functions and classes yet. Please bear with me while I continue to work on this in my spare time.
Also the test folder is empty... Because who needs testing......

### Copyright:
NHL and the NHL Shield are registered trademarks of the National Hockey League. NHL and NHL team marks are the property of the NHL and its teams. © NHL 2020. All Rights Reserved.