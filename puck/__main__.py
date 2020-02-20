#! /usr/bin/env python3.7
import sys
import os
from pathlib import Path
import json
from puck.database.db import connect_db
from puck.utils import ConfigError

PYTHONPATH = os.environ['PYTHONPATH']

CONFIG_PATH = Path(PYTHONPATH + '/puck/config.json')
CONFIG = ''

# check if config file exists
if not CONFIG_PATH.exists():
    raise ConfigError('No config file detected.')

# open config and load the data
f = open(CONFIG_PATH, 'r')

CONFIG = json.load(f)

f.close()

# these values are required for successful start up
try:
    db_path = Path(PYTHONPATH + CONFIG.pop('dbPath'))
    db_file = Path(CONFIG.pop('dbFile'))

    # create the full path
    full_path = db_path.joinpath(db_file)
    CONFIG.setdefault('dbPath', full_path.__str__())

    # make sure to create the path if it doesn't exist already
    if not db_path.exists():
        print(f'Creating path to Database file: {db_path}')
        # creates all directories that don't exist in the path
        db_path.mkdir(parents=True)

    # create the db file
    if not full_path.exists():
        print(f'Creating database file: {db_file}')
        full_path.touch()

except KeyError as err:
    raise ConfigError(f'Key: {err} was not found in config file.')

# set up environment
for cfg in CONFIG:
    os.environ[cfg] = CONFIG[cfg]


# get correct entry point ie CLI or TUI
if True:
    import puck.app
    main = puck.app.main
else:
    import puck.cli
    main = puck.cli.main

main()
