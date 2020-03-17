#! /usr/bin/env python3.7
import json
import os
import sys
from pathlib import Path

import puck.database.db
from puck.utils import ConfigError


CONFIG_PATH = Path(Path.home().joinpath('.puck/config.json'))
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
    CONFIG['dbName']
    CONFIG['dbUser']
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
