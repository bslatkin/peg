import grammar
import parameters
import parser
import reader



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


def describe_error(handlers, syntax_node):
    handle_args = []
    handle_kwargs {}

    for key, value in syntax_node.value:
        if isinstance(value, syntax.SyntaxNode):
            checked_value = describe_error(handlers, value)
            if isinstance(key, int):
                handle_args.append(checked_value)
            else:
                handle_kwargs[key] = checked_value
        else:
            if isinstance(key, int):
                handle_args.append(value)
            else:
                handle_kwargs[key] = value

    node_type = type(value)
    handler = handlers[value_type]
    return handler(*handle_args, **handle_kwargs)
