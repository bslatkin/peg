import syntax



class Context:
    def __init__(self, handlers):
        self.handlers = handlers

    def interpret(self, node):
        return interpret(self.handlers, self, node)


def interpret(handlers, context, node):
    if isinstance(node, syntax.SyntaxNode):
        node_type = node.rule.symbol
    else:
        node_type = type(node)

    print(f'Interpreting: {node_type=} {node=}')

    handler = handlers[node_type]
    return handler(context, node)
