from typing import List


class FakeFile:
    def __init__(self, data: List[str]):
        self.data = data
        self.line = 0
        self.column = 0

    def get_slice(self, line, start, size):
        if line >= len(self.data):
            return b''

        if size == -1:
            return self.data[line][start:].encode('utf-8')

        if size < len(self.data[line]) - start:
            return b''

        return self.data[line][start: start + size].encode('utf-8')

    def read(self, n: int = 1) -> bytes:
        length = len(self.data[self.line]) - self.column

        if length > n:
            part = self.get_slice(self.line, self.column, n)
            self.column += n
            return part
        else:
            first_part = self.get_slice(self.line, self.column, -1)
            remaining = n - (length - self.column)

            if self.line + 1 == len(self.data):
                return first_part

            self.line += 1
            self.column = min(remaining, len(self.data[self.line]))
            second_part = self.get_slice(self.line, 0, self.column)
            return first_part + second_part

    def readable(self, *args, **kwargs) -> bool:
        return True

    def writeable(self, *args, **kwargs) -> bool:
        return False

    def readline(self, *args, **kwargs) -> bytes:
        line = self.data[self.line][self.column:]

        if self.line + 1 < len(self.data):
            self.line += 1
            self.column = 0

        return line.encode('utf-8')

    def __iter__(self):
        part = self.get_slice(self.line, self.column, -1)
        self.line += 1
        self.column = 0
        yield part

        for line in self.data[self.line:]:
            yield line.encode('utf-8')


if __name__ == '__main__':

    import pandas as pd

    f = FakeFile([
        'a,b\n',
        '1,2\n'
    ])

    # for line in f:
    #    print(line)

    print(pd.read_csv(f))
