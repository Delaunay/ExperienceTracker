"""
    Provide a way to intercept print calls, to save output inside the db
"""

default_print = print


def track_print(self, *args, sep=' ', end='\n', file=None):
    default_print('track_printing')
    default_print(self, *args, sep=sep, end=end, file=None)


print = track_print


if __name__ == '__main__':
    print('test')
