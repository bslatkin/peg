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
        self.assertEqual((1, 1), value.column_range())

    def test_blank_line_start(self):
        source = reader.Source(self.path, '\n\nhello\nthere\n')
        value = reader.Value(source, 'hello', 2, 6)
        self.assertEqual(1, value.line_start_index())
        self.assertEqual(5, value.line_end_index())
        self.assertEqual(2, value.line_start_number())
        self.assertEqual('hello', value.text_lines())
        self.assertEqual((1, 5), value.column_range())

    def test_blank_line_end(self):
        pass

    def test_value_multiple_lines(self):
        pass

    def test_first_column(self):
        pass

    def test_middle_column(self):
        pass

    def test_last_column(self):
        pass

    def test_full_column_span(self):
        pass

    def test_value_all_lines(self):
        pass


if __name__ == '__main__':
    unittest.main()
