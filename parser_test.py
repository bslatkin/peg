import unittest

import grammar
from grammar import Ref, Expr, Choice, ZeroOrMore, OneOrMore, Optional
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

    def run_test(self, text):
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


class ParseFailureTest(TestBase):

    def test_all_leftover(self):
        with self.assertRaises(parser.InputRemainingError) as context:
            self.run_test('+1+2')

        exc = context.exception

        self.assertIsNone(exc.node)
        self.assertEqual('+', exc.value.text)
        self.assertEqual('+1+2', exc.value.text_lines())

    def test_some_leftover(self):
        with self.assertRaises(parser.InputRemainingError) as context:
            self.run_test('(1+2)-')

        exc = context.exception

        found = flatten(exc.node)
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

        self.assertEqual('-', exc.value.text)
        self.assertEqual('(1+2)-', exc.value.text_lines())


if __name__ == '__main__':
    unittest.main()
