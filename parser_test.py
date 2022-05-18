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

    def run_test(self, text, *, rules=None):
        if rules is None:
            rules = get_rules()
        buffer = reader.get_string_reader(text)
        result = parser.parse(rules, buffer)
        found = flatten(result)
        return found


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
        self.assertEqual(expected, found)

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
        self.assertEqual(expected, found)

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
        with self.assertRaises(parser.NothingMatchesError) as context:
            self.run_test('+1+2')

        exc = context.exception

        value, next_reader = exc.remaining.read()
        self.assertEqual('+1+2', value.text)
        self.assertEqual('+1+2', value.text_lines())

    def test_trailing_leftover(self):
        with self.assertRaises(parser.IncompleteParseError) as context:
            self.run_test('(1+2)-')

        exc = context.exception

        found = flatten(exc.node)
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
        self.assertEqual(expected, found)

        reader_values = parser.get_combined_reader_value(exc.node)
        self.assertEqual('(1+2)-', reader_values.text)
        self.assertEqual('(1+2)-', reader_values.text_lines())

        value, next_reader = exc.node.remaining.read()
        self.assertEqual('', value.text)

    def test_middle_leftover(self):
        with self.assertRaises(parser.IncompleteParseError) as context:
            x = self.run_test('1+nope')

        exc = context.exception

        found = flatten(exc.node)
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
        self.assertEqual(expected, found)

        reader_values = parser.get_combined_reader_value(exc.node)
        self.assertEqual('1+', reader_values.text)
        self.assertEqual('1+nope', reader_values.text_lines())

        value, next_reader = exc.node.remaining.read()
        self.assertEqual('nope', value.text)

    def test_many_partial_choices(self):
        with self.assertRaises(parser.IncompleteParseError) as context:
            x = self.run_test('12z', rules=get_partial_choice_rules())

        exc = context.exception

        found = flatten(exc.node)
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
        self.assertEqual(expected, found)

        reader_values = parser.get_combined_reader_value(exc.node)
        self.assertEqual('12', reader_values.text)
        self.assertEqual('12z', reader_values.text_lines())

        value, next_reader = exc.node.remaining.read()
        self.assertEqual('z', value.text)


if __name__ == '__main__':
    unittest.main()
