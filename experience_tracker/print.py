"""
    Provide a way to intercept print calls, to save output inside the db
"""

default_print = print
out = []
err = []


def track_print(self, *args, sep=' ', end='\n', file=None):
    default_print(self, *args, sep=sep, end=end, file=file)
    out.append(str(self) + sep.join(args))


print = track_print


if __name__ == '__main__':
    print('test')
