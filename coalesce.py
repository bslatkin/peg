import grammar
import parameters
import parser
import reader



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
