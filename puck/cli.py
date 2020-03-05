import arrow
import click

from puck.database.db import connect_db
from puck.games_handler import games_handler
from puck.utils import style


class Config(object):
    """
    Holds all top level options
    """

    def __init__(self, conn, verbose=False, output_file=None):
        self.verbose = verbose
        self.output_file = output_file
        self.conn = conn


class MutuallyExclusiveOption(click.Option):
    """
    This class is used to make options mutually exclusive.

    Thanks to this Stack Overflow Answer:
    https://stackoverflow.com/questions/37310718/mutually-exclusive-option-groups-in-python-click   # noqa

    Additional thanks to the Watson CLI program for help in adding the _exclusive_error function
    https://github.com/TailorDev/Watson/blob/master/watson/cli.py
    """

    def __init__(self, *args, **kwargs):
        self.mutually_exclusive = set(kwargs.pop('mutually_exclusive', []))
        super(MutuallyExclusiveOption, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        if self.mutually_exclusive.intersection(opts) and self.name in opts:
            self._exclusive_error()

        return super(MutuallyExclusiveOption, self).handle_parse_result(
            ctx, opts, args
        )

    def _exclusive_error(self):
        self.mutually_exclusive.add(self.opts[-1].strip('-'))
        errmsg = 'The following options are mutually exclusive: '
        '{}'.format(', '.join(
            ['--{}'.format(_) for _ in self.mutually_exclusive]))
        raise click.ClickException(
            style(errmsg, 'error')
        )


class ISODateType(click.ParamType):
    """
    ISODate type is YYYY-MM-DD format mainly used in the games command.
    NOTE: only need Year in YYYY format. MM and DD can pass without
        leading zeroes.
    """
    name = 'date'

    def convert(self, value, param, ctx):
        # required function for click.ParamType
        # returns value or invokes exception
        if value and self._is_valid_input(value):
            return value

        errmsg = f'Invalid input: {value}. Please use the ISO' \
            'Date format YYYY-MM-DD.\n       ' \
            'Please make sure input is a valid date.'
        raise click.ClickException(style(errmsg, 'error'))

    def _is_valid_input(self, value):
        # simply attempt to create an arrow object with the input
        # if it fails, return false
        try:
            # this format can extend to YYYY-MM-DD
            arrow.get(value, 'YYYY-M-D')
        except ValueError as e:
            return False
        except arrow.parser.ParserMatchError as e:
            return False

        return True


# pass_config = click.make_pass_decorator(Config)
Date = ISODateType()
File = click.File()


@click.group()
@click.option('-v', '--verbose', is_flag=True, help='Prints verbose output')
@click.option(
    '-o', '--output-file', nargs=1, type=File,
    help='Outputs results to CSV file at specified file location'
)
@click.pass_context
def cli(ctx, verbose, output_file):
    conn = connect_db()
    ctx.obj = Config(conn, verbose, output_file)


@cli.command()
@click.argument(
    'team', default=None, required=False,
)
@click.option(
    '-t', '--today', is_flag=True,
    help='Query Today\'s games (Local Time)', cls=MutuallyExclusiveOption,
    mutually_exclusive=['yesterday', 'tomorrow', 'date', 'date_range']
)
@click.option(
    '-y', '--yesterday', is_flag=True,
    help='Query Yesterday\'s games (Local Time)', cls=MutuallyExclusiveOption,
    mutually_exclusive=['today', 'tomorrow', 'date', 'date_range']
)
@click.option(
    '--tomorrow', is_flag=True,
    help='Query Tomorrow\'s games (Local Time)', cls=MutuallyExclusiveOption,
    mutually_exclusive=['today', 'yesterday', 'date', 'date_range']
)
@click.option(
    '-d', '--date', required=False, nargs=1, type=Date,
    help='Query specific date (YYYY-MM-DD)', cls=MutuallyExclusiveOption,
    mutually_exclusive=['today', 'yesterday', 'tomorrow', 'date_range']
)
@click.option(
    '-r', '--date-range', required=False, nargs=2, type=Date,
    help='Query a date range (YYYY-MM-DD) to (YYYY-MM-DD)', cls=MutuallyExclusiveOption,  # noqa
    mutually_exclusive=['today', 'yesterday', 'tomorrow', 'date']
)
@click.pass_context
def games(ctx, team, today, yesterday, tomorrow, date, date_range):
    """Queries the NHL schedule. To query for a specific team
     use 3-Letter abberviation TEAM.

     TODO: Possible "Finished" game option
     """
    cmd_vals = {k: v for k, v in ctx.params.items() if v}
    games_handler(ctx.obj, cmd_vals)


# enter cli
def main():
    cli()
