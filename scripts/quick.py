import puck.utils as pu
import json


with open('./teams.json', 'w') as f:
    r = pu._get_url('stats')
    final = dict()
    for team in r['teams']:
        final.setdefault(team['name'], team['abbreviation'])
    json.dump(final, f)

