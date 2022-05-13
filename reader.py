
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
        for i in range(self.start - 1, -1, -1):
            if self.source.data[i] == '\n':
                break

        return i + 1

    def line_end_index(self):
        for i in range(self.end, len(self.source.data)):
            if self.source.data[i] == '\n':
                break

        return i - 1

    def line_start_number(self):
        before = self.source.data[:self.start]
        return before.count('\n')

    def text_lines(self):
        line_start_index = self.line_start_index()
        line_end_index = self.line_end_index()
        return self.source.data[line_start_index:line_end_index + 1]

    def column_range(self):
        line_start_index = self.line_start_index()
        start_number = self.start - line_start_index
        end_number = self.end - line_start_index
        return start_number, end_number


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
