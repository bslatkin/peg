import sys

import parser
import syntax


class Error:
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

    return ''.join(buffer)


def print_parse_error(e):
    pass


def print_interpret_error(e):
    pass


def repl_one(rules, context, source):
    parse_tree = parser.parse(rules, source)
    error = parser.get_parse_error(parse_tree)
    if error:
        print_parse_error(error)
        return

    syntax_tree = syntax.coalesce(parse_tree)
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
