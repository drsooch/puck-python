"""
Miscellaneous debug functions.
"""


def debug(file, msg):
    with open(file, 'w') as f:
        f.write(str(msg))
