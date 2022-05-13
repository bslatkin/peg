import grammar
import parameters



class Error(Exception):
    pass


class InputRemainingError(Error):
    def __init__(self, value):
        self.value = value


class ParseNode:
    def __init__(self, source, value, remaining):
        self.source = source
        self.value = value
        self.remaining = remaining

    def __repr__(self):
        name = f'{self.source.__class__.__name__}('
        if isinstance(self.source, grammar.Rule):
            name = f'{name}{self.source.symbol!r}, '

        return (
            f'{name}'
            f'value={self.value!r}, '
            f'len(remaining)={len(self.remaining)})')


def descend_rule(rule, buffer):
    node = descend(rule.expr, buffer)
    if node is None:
        return None

    return ParseNode(rule, node, node.remaining)


def match_params(source, params, buffer):
    found = parameters.Params()
    current = buffer

    for key, value in params:
        node = descend(value, current)
        if node is None:
            return None

        found.assign(key, node)
        current = node.remaining

    return ParseNode(source, found, current)


def descend_expr(expr, buffer):
    return match_params(expr, expr.params, buffer)


def repeat_match_params(source, params, buffer):
    found = parameters.Params()
    current = buffer
    index = 0

    while current:
        node = match_params(source, params, current)
        if node is None:
            break

        found.assign(index, node)
        current = node.remaining
        index += 1

    return found, current


def descend_one_or_more(expr, buffer):
    pairs = list(expr.params)
    assert len(pairs) == 1
    index, sub_expr = pairs[0]
    assert index == 0

    found, remaining = repeat_match_params(sub_expr, sub_expr.params, buffer)

    if not found:
        return None

    return ParseNode(expr, found, remaining)


def descend_zero_or_more(expr, buffer):
    pairs = list(expr.params)
    assert len(pairs) == 1
    index, sub_expr = pairs[0]
    assert index == 0

    found, remaining = repeat_match_params(sub_expr, sub_expr.params, buffer)
    return ParseNode(expr, found, remaining)


def descend_optional(expr, buffer):
    node = match_params(expr, expr.params, buffer)
    if node is not None:
        return ParseNode(expr, node, node.remaining)

    return ParseNode(expr, None, buffer)


def descend_and(expr, buffer):
    node = match_params(expr, expr.params, buffer)
    if node is None:
        return None

    return ParseNode(expr, node, buffer)


def descend_not(expr, buffer):
    node = match_params(expr, expr.params, buffer)
    if node is not None:
        return None

    return ParseNode(expr, None, buffer)


def descend_choice(expr, buffer):
    found = parameters.Params()
    node = None

    for key, value in expr.params:
        if node is None:
            node = descend(value, buffer)
            found.assign(key, node)
        else:
            found.assign(key, None)

    if node is None:
        return None

    return ParseNode(expr, found, node.remaining)


def descend_str(expr, buffer):
    value, remaining = buffer.read(len(expr))
    if expr != value.text:
        return None

    return ParseNode(expr, value, remaining)


VISITORS = {
    grammar.And: descend_and,
    grammar.Choice: descend_choice,
    grammar.Expr: descend_expr,
    grammar.Not: descend_not,
    grammar.OneOrMore: descend_one_or_more,
    grammar.Optional: descend_optional,
    grammar.Rule: descend_rule,
    str: descend_str,
    grammar.ZeroOrMore: descend_zero_or_more,
}


def descend(item, buffer):
    print(f'Descending: {item=}, {type(item)=} with {buffer=}')
    visitor = VISITORS[type(item)]
    return visitor(item, buffer)


def check_parse_error(remaining):
    if not remaining:
        return

    first_extra, _ = remaining.read(1)
    raise InputRemainingError(first_extra)


def parse(rules, buffer):
    for rule in rules:
        node = descend(rule, buffer)
        if node is not None:
            check_parse_error(node.remaining)
            return node

    check_parse_error(buffer)
    assert False, 'Not reached'
