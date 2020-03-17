"""
This is the main setup file for Puck.
"""

from pathlib import Path
import subprocess
import json
import psycopg2 as pg

PUCK = Path.home().joinpath('.puck/')

print('Creating Configuration file...')
if Path.exists(PUCK):
    for file in Path.iterdir(PUCK):
        Path.unlink(file)
    Path.rmdir(PUCK)

Path.mkdir(PUCK)

Path.touch(PUCK.joinpath('config.json'))
print(
    """NOTE: Please make sure you have set up a database for puck.
I have not been able to get Postgres to cooperate to allow for generic \
database and user creation."""
)
connected = False

with open(PUCK.joinpath('config.json'), 'w') as f:
    while not connected:
        db_name = input('Please enter the name of the database created\n> ')
        db_user = input(
            'Please enter the name of the user associated with the DB\n> '
        )

        try:
            pg.connect(database=db_name, user=db_user)
        except pg.OperationalError as err:
            if db_name in str(err):
                print(f'{db_name} is not a valid database.')
            elif db_user in str(err):
                print(f'{db_user} is not a valid username.')
        else:
            connected = True

    json.dump({'dbName': db_name, 'dbUser': db_user}, f)
