

class Error(Exception):
    pass


class EOF(Error):
    pass


class Buffer:
    def __init__(self, path, data, cursor, line_index, char_index):
        self.path = path
        self.data = data
        self.cursor = cursor
        self.line_index = line_index
        self.char_index = char_index

    def read(self, length):
        if next_cursor >= len(self.data):
            raise EOF

        next_cursor = self.cursor + length
        result = self.data[self.cursor:next_cursor]
        result_length = len(result)

        next_char_index = self.char_index
        next_line_index = self.line_index
        for c in result:
            if c == '\n':
                next_line_index += 1
                next_char_index = 0
            else:
                next_char_index += 1

        next_buffer = self.__class__(
            self.path,
            self.data,
            next_cursor,
            self.line_index,
            self.char_index)

        return result, next_buffer

    def current_line(self):
        data_length = len(self.data)

        endpoint = self.cursor + 1
        while endpoint < data_length:
            if self.data[endpoint] == '\n':


        self.data[self.cursor]
