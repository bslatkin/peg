import sys

import parser
import reader
import syntax


class Error(Exception):
    pass


class InterpretError(Error):
    def __init__(self, reason, value):
        super().__init__(reason, value)
        self.reason = reason
        self.value = value


class Context:
    def __init__(self, handlers):
        self.handlers = handlers

    def interpret(self, value):
        return interpret(self.handlers, self, value)


def interpret(handlers, context, value):
    if isinstance(value, syntax.SyntaxNode):
        value_type = value.rule.symbol
        to_handle = value.value
    else:
        value_type = type(value)
        to_handle = value

    print(f'Interpreting: {value_type=} {to_handle=}')

    handler = handlers[value_type]
    try:
        return handler(context, to_handle)
    except InterpretError:
        raise  # Pass through unmodified
    except Exception as e:
        raise InterpretError(e, to_handle)


def read_input():
    sys.stdout.write('> ')
    sys.stdout.flush()
    buffer = []
    empty_lines = 0
    while True:
        line = sys.stdin.readline()
        if not line.strip():
            empty_lines += 1
            if empty_lines == 2:
                break
        else:
            empty_lines = 0
            buffer.append(line)

        sys.stdout.write('* ')
        sys.stdout.flush()

    joined_str = ''.join(buffer).rstrip()

    return reader.get_string_reader(joined_str)


def print_parse_error(e):
    value = e.value

    path = value.source.path

    lines = value.text_lines()
    line_number = value.line_start_number()

    column_start = value.column_start_index()
    column_end = value.column_end_index()
    run_length = column_end - column_start

    before = ' ' * column_start
    under = '^' * run_length
    underline = f'{before}{under}'

    print(f'Error on {path}:{line_number}: {e.__class__.__name__}')
    print(lines)
    print(underline)


def print_interpret_error(e):
    breakpoint()


def repl_one(rules, context, source):
    try:
        parse_tree = parser.parse(rules, source)
    except parser.Error as e:
        print_parse_error(e)
        return

    syntax_tree = syntax.coalesce(parse_tree)
    print(syntax_tree)
    try:
        result = context.interpret(syntax_tree)
    except InterpretError as e:
        print_interpret_error(e)
        return

    print(result)


def repl(rules, context):
    try:
        while True:
            source = read_input()
            repl_one(rules, context, source)
    except KeyboardInterrupt:
        print('Terminating')
