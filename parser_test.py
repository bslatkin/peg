import unittest

import grammar
from grammar import Ref, Expr, Choice, ZeroOrMore, OneOrMore, Optional, And
import parameters
import parser
import reader



def get_rules():
    rules = {
        'Sum': Expr(
            left=Ref('Value'),
            suffix=ZeroOrMore(
                operator=Choice('+', '-'),
                right=Ref('Sum'))),

        'Value': Choice(
            digits=OneOrMore(Ref('Number')),
            sub_expr=Expr(
                left_paren='(',
                inner_sum=Ref('Sum'),
                right_paren=')')),

        'Number': Choice('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'),
    }
    resolved = grammar.resolve_refs(rules)
    return resolved


def get_partial_choice_rules():
    rules = {
        'Value': Choice(
            first=Expr(Ref('Int'), Ref('Int'), Ref('Int'), And('x')),
            second=Expr(Ref('Int'), Ref('Int'), And('y'))),

        'Int': Choice('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'),
    }
    resolved = grammar.resolve_refs(rules)
    return resolved


def flatten(node):
    if isinstance(node, parser.ParseNode):
        return flatten(node.value)

    if isinstance(node, parameters.Params):
        return [(k, flatten(v)) for k, v in node.mappings.items()]

    if isinstance(node, reader.Value):
        return node.text

    return node


class TestBase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def run_test(self, text, *, rules=None, result_type=parser.Match):
        if rules is None:
            rules = get_rules()
        buffer = reader.get_string_reader(text)
        result = parser.parse(rules, buffer)
        self.assertIsInstance(result, result_type)
        return result

    def assertRemaining(self, node, expected):
        remaining_value, _ = node.remaining.read()
        self.assertEqual(expected, remaining_value.text)

    def assertReaderValue(self, node, *, text, lines):
        reader_value = node.reader_value()
        self.assertEqual(text, reader_value.text)
        self.assertEqual(lines, reader_value.text_lines())


class ParseSuccessTest(TestBase):

    def test_basic(self):
        found = self.run_test('1')
        expected = \
            [('digits',
              [(0,
                [(0,
                  [(0, None),
                   (1, '1'),
                   (2, None),
                   (3, None),
                   (4, None),
                   (5, None),
                   (6, None),
                   (7, None),
                   (8, None),
                   (9, None)])])]),
             ('sub_expr', None)]
        self.assertEqual(expected, flatten(found))

        self.assertRemaining(found, '')

    def test_multiple_levels(self):
        found = self.run_test('(1+2)')
        expected = \
            [('digits', None),
             ('sub_expr',
              [('left_paren', '('),
               ('inner_sum',
                [('left',
                  [('digits',
                    [(0,
                      [(0,
                        [(0, None),
                         (1, '1'),
                         (2, None),
                         (3, None),
                         (4, None),
                         (5, None),
                         (6, None),
                         (7, None),
                         (8, None),
                         (9, None)])])]),
                   ('sub_expr', None)]),
                 ('suffix',
                  [(0,
                    [('operator', [(0, '+'), (1, None)]),
                     ('right',
                      [('left',
                        [('digits',
                          [(0,
                            [(0,
                              [(0, None),
                               (1, None),
                               (2, '2'),
                               (3, None),
                               (4, None),
                               (5, None),
                               (6, None),
                               (7, None),
                               (8, None),
                               (9, None)])])]),
                         ('sub_expr', None)]),
                       ('suffix', [])])])])]),
               ('right_paren', ')')])]
        self.assertEqual(expected, flatten(found))

        self.assertRemaining(found, '')

    def test_and_match(self):
        self.fail()

    def test_and_miss(self):
        self.fail()

    def test_not_match(self):
        self.fail()

    def test_not_miss(self):
        self.fail()

    def test_optional_match(self):
        self.fail()

    def test_optional_miss(self):
        self.fail()


class ParseFailureTest(TestBase):

    def test_all_leftover(self):
        found = self.run_test('+1+2', result_type=parser.Miss)
        self.assertIsNone(found.value)
        self.assertRemaining(found, '+1+2')

    def test_trailing_leftover(self):
        found = self.run_test('(1+2)-', result_type=parser.Partial)
        expected = \
            [('left',
              [('digits', None),
               ('sub_expr',
                [('left_paren', '('),
                 ('inner_sum',
                  [('left',
                    [('digits',
                      [(0,
                        [(0,
                          [(0, None),
                           (1, '1'),
                           (2, None),
                           (3, None),
                           (4, None),
                           (5, None),
                           (6, None),
                           (7, None),
                           (8, None),
                           (9, None)])])]),
                     ('sub_expr', None)]),
                   ('suffix',
                    [(0,
                      [('operator', [(0, '+'), (1, None)]),
                       ('right',
                        [('left',
                          [('digits',
                            [(0,
                              [(0,
                                [(0, None),
                                 (1, None),
                                 (2, '2'),
                                 (3, None),
                                 (4, None),
                                 (5, None),
                                 (6, None),
                                 (7, None),
                                 (8, None),
                                 (9, None)])])]),
                           ('sub_expr', None)]),
                         ('suffix', [])])])])]),
                 ('right_paren', ')')])]),
             ('suffix',
                [(0, [('operator', [(0, None), (1, '-')]), ('right', None)])])]
        self.assertEqual(expected, flatten(found))

        self.assertReaderValue(found, text='(1+2)-', lines='(1+2)-')
        self.assertRemaining(found, '')

    def test_middle_leftover(self):
        found = self.run_test('1+nope', result_type=parser.Partial)
        expected = \
            [('left',
              [('digits',
                [(0,
                  [(0,
                    [(0, None),
                     (1, '1'),
                     (2, None),
                     (3, None),
                     (4, None),
                     (5, None),
                     (6, None),
                     (7, None),
                     (8, None),
                     (9, None)])])]),
               ('sub_expr', None)]),
             ('suffix', [(0,
                [('operator', [(0, '+'), (1, None)]), ('right', None)])])]
        self.assertEqual(expected, flatten(found))

        self.assertReaderValue(found, text='1+', lines='1+nope')
        self.assertRemaining(found, 'nope')

    def test_many_partial_choices(self):
        found = self.run_test(
            '12z',
            rules=get_partial_choice_rules(),
            result_type=parser.Partial)

        expected = \
            [('first',
              [(0,
                [(0, None),
                 (1, '1'),
                 (2, None),
                 (3, None),
                 (4, None),
                 (5, None),
                 (6, None),
                 (7, None),
                 (8, None),
                 (9, None)]),
               (1,
                [(0, None),
                 (1, None),
                 (2, '2'),
                 (3, None),
                 (4, None),
                 (5, None),
                 (6, None),
                 (7, None),
                 (8, None),
                 (9, None)]),
               (2, None)]),
             ('second',
              [(0,
                [(0, None),
                 (1, '1'),
                 (2, None),
                 (3, None),
                 (4, None),
                 (5, None),
                 (6, None),
                 (7, None),
                 (8, None),
                 (9, None)]),
               (1,
                [(0, None),
                 (1, None),
                 (2, '2'),
                 (3, None),
                 (4, None),
                 (5, None),
                 (6, None),
                 (7, None),
                 (8, None),
                 (9, None)]),
               (2, None)])]
        self.assertEqual(expected, flatten(found))

        self.assertReaderValue(found, text='12', lines='12z')
        self.assertRemaining(found, 'z')


if __name__ == '__main__':
    unittest.main()
