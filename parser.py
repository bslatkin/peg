import grammar



class Node:
    def __init__(self, value, remaining):
        self.value = value
        self.remaining = remaining

    def __str__(self):
        if self.value is None:
            return ''

        if isinstance(self.value, (list, tuple)):
            return ''.join(str(i) for i in self.value)

        return str(self.value)

    def __repr__(self):
        return (
            f'{self.__class__.__name__}'
            f'(value={self.value!r}, '
            f'len(remaining)={len(self.remaining)})')


class StrNode(Node):
    pass


class ExprNode(Node):
    pass


class OneOrMoreNode(Node):
    pass


class ZeroOrMoreNode(Node):
    pass


class OptionalNode(Node):
    pass


class AndNode(Node):
    pass


class NotNode(Node):
    pass


class RuleNode(Node):
    def __init__(self, rule, value, remaining):
        super().__init__(value, remaining)
        self.rule = rule

    def __repr__(self):
        return f'{self.rule.symbol}({self.value})'



def descend_rule(rule, buffer):
    node = descend(rule.expr, buffer)
    if node is None:
        return None

    return RuleNode(rule, node, node.remaining)


def match_items(items, buffer):
    found = []
    current = buffer
    for item in items:
        node = descend(item, current)
        if node is None:
            return None

        found.append(node)
        current = node.remaining

    return ExprNode(found, current)


def descend_expr(expr, buffer):
    return match_items(expr.items, buffer)


def repeat_match_items(items, buffer):
    found = []
    current = buffer
    while current:
        node = match_items(items, current)
        if node is None:
            break

        found.append(node)
        current = node.remaining

    return found, current


def descend_one_or_more(expr, buffer):
    found, remaining = repeat_match_items(expr.items, buffer)

    if not found:
        return None

    return OneOrMoreNode(found, remaining)


def descend_zero_or_more(expr, buffer):
    found, remaining = repeat_match_items(expr.items, buffer)
    return ZeroOrMoreNode(found, remaining)


def descend_optional(expr, buffer):
    node = match_items(expr.items, buffer)
    if node is not None:
        return OptionalNode(node, node.remaining)

    return OptionalNode(None, buffer)


def descend_and(expr, buffer):
    node = match_items(expr.items, buffer)
    if not node:
        return None

    return AndNode(node, buffer)


def descend_not(expr, buffer):
    node = match_items(expr.items, buffer)
    if node is not None:
        return None

    return NotNode(None, buffer)


def descend_choice(expr, buffer):
    for item in expr.items:
        node = descend(item, buffer)
        if node is not None:
            return node

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
    return StrNode(consumed, remaining)


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

