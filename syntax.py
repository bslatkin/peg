import grammar
import parser



class SyntaxNode:
    def __init__(self, rule, value):
        self.rule = rule
        self.value = value

    def __repr__(self):
        return (
            f'{self.rule.symbol}('
            f'{self.value!r})')


def coalesce_params(value):
    result = grammar.Params()

    for key, other_value in value:
        flattened = coalesce(other_value)

        if flattened is None:
            continue

        result.assign(key, flattened)

    if not result:
        return None

    # xxx clean this up
    if (len(result.mappings) == 1 and
            0 in result.mappings):
        return result.mappings[0]

    return result


def coalesce(node):
    print(f'Coalescing: {node=}, {type(node)=}')
    if node is None:
        return None

    if (isinstance(node, parser.ParseNode) and
          isinstance(node.source, grammar.Rule)):
        flattened = coalesce(node.value)
        return SyntaxNode(node.source, flattened)

    if isinstance(node, grammar.Params):
        return coalesce_params(node)

    if isinstance(node, str):
        return node

    return coalesce(node.value)
