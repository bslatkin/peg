import unittest

import reader


class ValueTest(unittest.TestCase):

    def setUp(self):
        self.path = 'my/path'

    def test_empty(self):
        source = reader.Source(self.path, '')
        value = reader.Value(source, '', 0, 0)
        self.assertEqual(0, value.line_start_index())
        self.assertEqual(0, value.line_end_index())
        self.assertEqual(1, value.line_start_number())
        self.assertEqual('', value.text_lines())
        self.assertEqual(0, value.column_start_index())
        self.assertEqual(0, value.column_end_index())

    def test_blank_line_start(self):
        source = reader.Source(self.path, '\n\nhello there\nbanana\n')
        value = reader.Value(source, 'hello', 2, 6)
        self.assertEqual(2, value.line_start_index())
        self.assertEqual(13, value.line_end_index())
        self.assertEqual(3, value.line_start_number())
        self.assertEqual('hello there\n', value.text_lines())
        self.assertEqual(0, value.column_start_index())
        self.assertEqual(4, value.column_end_index())

    def test_blank_line_end(self):
        source = reader.Source(self.path, 'yes hello\n')
        value = reader.Value(source, 'hello', 4, 8)
        self.assertEqual(0, value.line_start_index())
        self.assertEqual(9, value.line_end_index())
        self.assertEqual(1, value.line_start_number())
        self.assertEqual('yes hello\n', value.text_lines())
        self.assertEqual(4, value.column_start_index())
        self.assertEqual(8, value.column_end_index())

    def test_no_blank_line_end(self):
        source = reader.Source(self.path, 'hello')
        value = reader.Value(source, 'hello', 0, 4)
        self.assertEqual(0, value.line_start_index())
        self.assertEqual(5, value.line_end_index())
        self.assertEqual(1, value.line_start_number())
        self.assertEqual('hello', value.text_lines())
        self.assertEqual(0, value.column_start_index())
        self.assertEqual(4, value.column_end_index())

    def test_value_multiple_lines(self):
        source = reader.Source(self.path, 'hello\nyes\n')
        value = reader.Value(source, 'hello\nyes', 0, 9)
        self.assertEqual(0, value.line_start_index())
        self.assertEqual(9, value.line_end_index())
        self.assertEqual(1, value.line_start_number())
        self.assertEqual('hello\nyes\n', value.text_lines())
        self.assertEqual(0, value.column_start_index())
        self.assertEqual(9, value.column_end_index())

    def test_first_column_in_line(self):
        source = reader.Source(self.path, 'hello\n')
        value = reader.Value(source, 'hello', 0, 4)
        self.assertEqual(0, value.line_start_index())
        self.assertEqual(5, value.line_end_index())
        self.assertEqual(1, value.line_start_number())
        self.assertEqual('hello\n', value.text_lines())
        self.assertEqual(0, value.column_start_index())
        self.assertEqual(4, value.column_end_index())

    def test_last_column_in_line(self):
        source = reader.Source(self.path, 'yes k\n')
        value = reader.Value(source, 'k', 4, 5)
        self.assertEqual(0, value.line_start_index())
        self.assertEqual(5, value.line_end_index())
        self.assertEqual(1, value.line_start_number())
        self.assertEqual('yes k\n', value.text_lines())
        self.assertEqual(4, value.column_start_index())
        self.assertEqual(5, value.column_end_index())

    def test_full_column_span(self):
        pass

    def test_value_covers_all_lines(self):
        pass

    def test_no_newlines(self):
        pass



if __name__ == '__main__':
    unittest.main()
