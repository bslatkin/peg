import grammar
import parameters
import parser
import reader



class Error(Exception):
    pass


class ValidationError(Error):
    def __init__(self, message, where):
        super().__init__(message, where)
        self.message = message
        self.where = where
        self.syntax_node = None


class SyntaxNode:
    def __init__(self, rule, value):
        self.rule = rule
        self.value = value

    def __repr__(self):
        if isinstance(self.value, parameters.Params):
            repr_string = parameters.repr_params(self.value)
        else:
            repr_string = repr(self.value)

        return (
            f'{self.rule.symbol}('
            f'{repr_string})')


def coalesce_params(value):
    result = parameters.Params()

    for key, other_value in value:
        flattened = coalesce(other_value)

        if flattened is None:
            continue

        result.assign(key, flattened)

    return result


def coalesce_repeated(value):
    result = []

    for _, other_value in value:
        flattened = coalesce(other_value)
        result.append(flattened)

    if not result:
        return None

    return result


def coalesce_rule(source, value):
    flattened = coalesce(value)
    return SyntaxNode(source, flattened)


def coalesce(node):
    print(f'Coalescing: {node=}, {type(node)=}')
    if node is None:
        return None

    if isinstance(node, parameters.Params):
        return coalesce_params(node)

    if isinstance(node, reader.Value):
        return node

    assert isinstance(node, parser.ParseNode)

    if isinstance(node.source, grammar.Rule):
        return coalesce_rule(node.source, node.value)

    if isinstance(node.source, grammar.RepeatedExpr):
        return coalesce_repeated(node.value)

    return coalesce(node.value)


# TODO: This is really an "explain" feature.
def validate(handlers, node):
    if isinstance(node, SyntaxNode):
        validate(handlers, node.value)
        handler = handlers[node.rule.symbol]
        try:
            handler(node.value)
        except ValidationError as e:
            e.syntax_node = node
            raise
    elif isinstance(node, parameters.Params):
        for key, value in node:
            validate(handlers, value)
    elif isinstance(node, list):
        for value in node:
            validate(handlers, value)
    else:
        pass  # TODO What should this do?
