"""
Miscellaneous debug functions.
"""


def debug(file, *msgs):
    with open(file, 'a') as f:
        for msg in msgs:
            f.write(msg)
            f.write('\n')
