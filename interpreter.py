import syntax



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
    return handler(context, to_handle)
