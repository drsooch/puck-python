import puck.puck.utils as utils
import json


def _main():
    # generate schedule json
    with open('../tests/JSON/Schedule.json', 'w') as f:
        j = utils._get_url(utils._SCHEDULE_URL)
        json.dump(j, f)

    # generate individual team json
    with open('../tests/JSON/Teams.json', 'w') as f:
        j = utils._get_url(utils._STATS_URL + f'/teams/{utils._TEAMS["NYR"]}')
        json.dump(j, f)

    # generate teams json
    with open('../tests/JSON/Teams.json', 'w') as f:
        j = utils._get_url(utils._STATS_URL + '/teams')
        json.dump(j, f)

    # generate franchise json
    with open('../tests/JSON/Franchises.json', 'w') as f:
        j = utils._get_url(utils._STATS_URL + '/franchises')
        json.dump(j, f)
