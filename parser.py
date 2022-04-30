import grammar



class ParseNode:
    def __init__(self, source, value, remaining):
        self.source = source
        self.value = value
        self.remaining = remaining

    def __str__(self):
        if self.value is None:
            return ''

        if isinstance(self.value, (list, tuple)):
            return ''.join(str(i) for i in self.value)

        return str(self.value)

    def __repr__(self):
        name = f'{self.source.__class__.__name__}('
        if isinstance(self.source, grammar.Rule):
            name = f'{name}{self.source.symbol}, '

        return (
            f'{name}'
            f'(value={self.value!r}, '
            f'len(remaining)={len(self.remaining)})')


def descend_rule(rule, buffer):
    node = descend(rule.expr, buffer)
    if node is None:
        return None

    return ParseNode(rule, node, node.remaining)


def match_items(source, items, buffer):
    found = []
    current = buffer
    for item in items:
        node = descend(item, current)
        if node is None:
            return None

        found.append(node)
        current = node.remaining

    return ParseNode(source, found, current)


def descend_expr(expr, buffer):
    return match_items(expr, expr.items, buffer)


def repeat_match_items(source, items, buffer):
    found = []
    current = buffer
    while current:
        # XXX This source is wrong, there should be an inner
        # Expr instance that the OneOrMore instance wraps.
        node = match_items(source, items, current)
        if node is None:
            break

        found.append(node)
        current = node.remaining

    return found, current


def descend_one_or_more(expr, buffer):
    found, remaining = repeat_match_items(expr, expr.items, buffer)

    if not found:
        return None

    return ParseNode(expr, found, remaining)


def descend_zero_or_more(expr, buffer):
    found, remaining = repeat_match_items(expr, expr.items, buffer)
    return ParseNode(expr, found, remaining)


def descend_optional(expr, buffer):
    node = match_items(expr, expr.items, buffer)
    if node is not None:
        return ParseNode(expr, node, node.remaining)

    return ParseNode(expr, None, buffer)


def descend_and(expr, buffer):
    node = match_items(expr, expr.items, buffer)
    if node is None:
        return None

    return ParseNode(expr, node, buffer)


def descend_not(expr, buffer):
    node = match_items(expr, expr.items, buffer)
    if node is not None:
        return None

    return ParseNode(expr, None, buffer)


def descend_choice(expr, buffer):
    for item in expr.items:
        node = descend(item, buffer)
        if node is not None:
            # TODO: This needs to carry through which
            # choice was picked so it can be acted on
            # appropriately later in the system.
            return ParseNode(expr, node, node.remaining)

    return None


def descend_str(expr, buffer):
    expr_length = len(expr)
    if expr_length > len(buffer):
        return None

    for i in range(expr_length):
        if expr[i] != buffer[i]:
            return None

    consumed = buffer[:expr_length]
    remaining = buffer[expr_length:]
    return ParseNode(expr, consumed, remaining)


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


def parse(rules, buffer):
    for rule in rules:
        node = descend(rule, buffer)
        if node is not None:
            return node

    return None
