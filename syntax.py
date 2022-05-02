import grammar
import parser



class SyntaxNode:
    def __init__(self, rule, value):
        self.rule = rule
        self.value = value

    def __repr__(self):
        if isinstance(self.value, grammar.Params):
            repr_string = grammar.repr_params(self.value)
        else:
            repr_string = repr(self.value)

        return (
            f'{self.rule.symbol}('
            f'{repr_string})')


def coalesce_params(value):
    result = grammar.Params()

    for key, other_value in value:
        flattened = coalesce(other_value)

        if flattened is None:
            continue

        if (isinstance(flattened, grammar.Params) and
                (flattened_list := flattened.as_list())):
            if len(flattened_list) == 1:
                result.assign(key, flattened_list[0])
            else:
                result.assign(key, flattened_list)
        else:
            result.assign(key, flattened)

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

    if (isinstance(node, parser.ParseNode) and
          isinstance(node.source, grammar.Rule)):
        return coalesce_rule(node.source, node.value)

    if isinstance(node, grammar.Params):
        return coalesce_params(node)

    if isinstance(node, str):
        return node

    return coalesce(node.value)
