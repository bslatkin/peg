
class Source:
    def __init__(self, path, data):
        self.path = path
        self.data = data


class Value:
    def __init__(self, source, text, start, end):
        self.source = source
        self.text = text
        self.start = start
        self.end = end

    def line_start_index(self):
        if not self.source.data:
            return 0

        i = self.start

        while i > 0:
            if self.source.data[i] == '\n':
                i += 1
                break
            else:
                i -= 1

        return i

    def line_end_index(self):
        if not self.source.data:
            return 0

        i = self.end

        while i < len(self.source.data):
            if self.source.data[i] == '\n':
                break
            else:
                i += 1

        # No trailing newline case
        if self.source.data and i == len(self.source.data):
            i -= 1

        return i

    def line_start_number(self):
        before = self.source.data[:self.start]
        return before.count('\n') + 1

    def text_lines(self):
        start = self.line_start_index()
        end = self.line_end_index() + 1
        return self.source.data[start:end]

    def column_start_index(self):
        line_start_index = self.line_start_index()
        return self.start - line_start_index

    def column_end_index(self):
        delta = self.end - self.start
        return self.column_start_index() + delta

    def __repr__(self):
        return f'{__name__}.{self.__class__.__name__}({self.text!r})'


class Reader:
    def __init__(self, source, index):
        self.source = source
        self.index = index

    def read(self, length):
        data_length = len(self.source.data)
        if self.index >= data_length:
            value = Value(self.source, '', data_length, data_length)
            return value, self

        next_index = self.index + length
        text = self.source.data[self.index:next_index]
        end_index = self.index + len(text)
        value = Value(self.source, text, self.index, end_index)

        next_reader = self.__class__(self.source, next_index)

        return value, next_reader

    def __repr__(self):
        remaining = self.source.data[self.index:]
        return f'{self.__class__.__name__}({remaining!r})'

    def __len__(self):
        return len(self.source.data) - self.index


def get_string_reader(data):
    source = Source('<string reader>', data)
    return Reader(source, 0)


def get_path_reader(path):
    with open(path) as f:
        data = f.read()

    source = Source(path, data)
    return Reader(source, 0)
