
class Source:
    def __init__(self, path, data):
        self.path = path
        self.data = data


class Buffer:
    def __init__(self, source, start, end):
        self.source = source
        self.start = start
        self.end = end


class Reader:
    def __init__(self, source, index):
        self.source = source
        self.index = index

    def read(self, length):
        data_length = len(self.source.data)
        if self.index >= data_length:
            buffer = Buffer(self.source, data_length, data_length)
            return buffer, self

        next_index = self.index + length
        result = self.source.data[self.index:next_index]
        result_length = len(result)

        end_index = self.index + result_length
        buffer = Buffer(self.source, index, end_index)

        next_reader = self.__class__(self.source, next_index)

        return buffer, next_reader

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
