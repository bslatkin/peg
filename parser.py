import grammar
import parameters
import reader


class Error(Exception):
    pass


class InputRemainingError(Error):
    def __init__(self, node, value):
        self.node = node
        self.value = value


class IncompleteParseError(Error):
    def __init__(self, node):
        self.node = node


class ParseNode:
    matched = True

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


class IncompleteNode(ParseNode):
    matched = False


def get_reader_values(node):
    if node is None:
        return []

    if isinstance(node.value, reader.Value):
        return [node.value]

    if isinstance(node.value, ParseNode):
        return get_reader_values(node.value)

    if isinstance(node.value, parameters.Params):
        result = []
        for _, other_value in node.value:
            result.extend(get_reader_values(other_value))
        return result


def get_combined_reader_value(node):
    values = get_reader_values(node)
    source = values[0].source
    min_start = min(v.start for v in values)
    max_end = max(v.end for v in values)
    text = source.data[min_start:max_end]
    return reader.Value(source, text, min_start, max_end)



def descend_rule(rule, buffer):
    node = descend(rule.expr, buffer)
    if not node.matched:
        return IncompleteNode(rule, node, node.remaining)

    return ParseNode(rule, node, node.remaining)


def match_params(source, params, buffer):
    found = parameters.Params()
    current = buffer
    match_success = False

    for key, value in params:
        node = descend(value, current)
        if node.matched:
            found.assign(key, node)
            match_success = True

        current = node.remaining

    if match_success:
        return ParseNode(source, found, current)
    else:
        return IncompleteNode(source, found, current )


def descend_expr(expr, buffer):
    return match_params(expr, expr.params, buffer)


def repeat_match_params(source, params, buffer):
    found = parameters.Params()
    current = buffer
    index = 0
    any_matches = False

    while current:
        node = match_params(source, params, current)

        if node.matched:
            any_matches = True
            found.assign(index, node)
        else:
            break

        current = node.remaining
        index += 1

    if any_matches:
        return ParseNode(source, found, current)
    else:
        return IncompleteNode(source, found, current)


def descend_one_or_more(expr, buffer):
    pairs = list(expr.params)
    assert len(pairs) == 1
    index, sub_expr = pairs[0]
    assert index == 0

    node = repeat_match_params(sub_expr, sub_expr.params, buffer)
    if node.matched:
        return ParseNode(expr, node, node.remaining)
    else:
        return IncompleteNode(expr, node, node.remaining)


def descend_zero_or_more(expr, buffer):
    pairs = list(expr.params)
    assert len(pairs) == 1
    index, sub_expr = pairs[0]
    assert index == 0

    node = repeat_match_params(sub_expr, sub_expr.params, buffer)
    return ParseNode(expr, node, node.remaining)


def descend_optional(expr, buffer):
    node = match_params(expr, expr.params, buffer)
    if node.matched:
        return ParseNode(expr, node, node.remaining)
    else:
        return ParseNode(expr, node, buffer)


def descend_and(expr, buffer):
    node = match_params(expr, expr.params, buffer)
    if node.matched:
        return ParseNode(expr, node, buffer)
    else:
        return IncompleteNode(expr, node, buffer)


def descend_not(expr, buffer):
    node = match_params(expr, expr.params, buffer)
    if node.matched:
        return IncompleteNode(expr, node, buffer)
    else:
        return ParseNode(expr, node, buffer)


def descend_choice(expr, buffer):
    found = parameters.Params()
    node = IncompleteNode(expr, found, buffer)

    for key, value in expr.params:
        if not node.matched:
            node = descend(value, buffer)
            if node.matched:
                found.assign(key, node)
                continue

    if node.matched:
        return ParseNode(expr, found, node.remaining)
    else:
        return IncompleteNode(expr, node, node.remaining)


def descend_str(expr, buffer):
    value, remaining = buffer.read(len(expr))
    if expr == value.text:
        return ParseNode(expr, value, remaining)
    else:
        return IncompleteNode(expr, value, remaining)


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
    if not buffer:
        return IncompleteNode(item, None, buffer)

    print(f'Descending: {item=}, {type(item)=} with {buffer=}')
    visitor = VISITORS[type(item)]
    return visitor(item, buffer)


def check_extra_error(node, remaining):
    if not remaining:
        return

    first_extra, _ = remaining.read(1)
    raise InputRemainingError(node, first_extra)


def pick_failure(full_size, failures):
    longest = full_size
    longest_node = None

    for node in failures:
        if len(node.remaining) < longest:
            longest = len(node.remaining)
            longest_node = node

    assert longest_node
    raise IncompleteParseError(longest_node)


def parse(rules, buffer):
    failures = []

    for rule in rules:
        node = descend(rule, buffer)
        if node.matched:
            check_extra_error(node, node.remaining)
            return node
        else:
            failures.append(node)

    pick_failure(len(buffer), failures)

    raise InputRemainingError(None, buffer)  # TODO test this
