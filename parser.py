import functools

import grammar
import parameters
import reader


class Error(Exception):
    pass


class NothingMatchesError(Error):
    def __init__(self, remaining):
        self.remaining = remaining


class IncompleteParseError(Error):
    def __init__(self, node):
        self.node = node


class ParseNode:
    matched = True

    def __init__(self, source, value, remaining):
        assert source is not None
        assert remaining is not None
        self.source = source
        self.value = value
        self.remaining = remaining

    def __repr__(self):
        name = f'{self.source.__class__.__name__}('
        if isinstance(self.source, grammar.Rule):
            name = f'{name}{self.source.symbol!r}, '

        return (
            f'{self.__class__.__name__}:{name}'
            f'value={self.value!r}, '
            f'remaining={self.remaining!r})')


class Match(ParseNode):
    pass


class Partial(ParseNode):
    pass


class Miss(ParseNode):
    pass


# TODO: Move this to reader.py
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


# TODO: Make this a better helper class behind a flag
DEPTH = 0

def trace(func):
    @functools.wraps(func)
    def wrapped(*args):
        global DEPTH
        prefix = DEPTH * '    '
        args_repr = ', '.join(repr(a) for a in args)
        print(f'{prefix} Running: {func.__name__}({args_repr})')
        DEPTH += 1
        result = func(*args)
        DEPTH -= 1
        print(f'{prefix} Result: {result!r}')
        return result
    return wrapped


@trace
def descend_rule(rule, buffer):
    node = descend(rule.expr, buffer)
    if isinstance(node, Match):
        return Match(rule, node, node.remaining)
    elif isinstance(node, Partial):
        return Partial(rule, node, node.remaining)
    else:
        return Miss(rule, None, buffer)


@trace
def match_params(source, params, buffer):
    found = parameters.Params()
    current = buffer

    consider_keys = 0
    match_keys = 0
    partial_keys = 0
    miss_keys = 0

    for key, value in params:
        consider_keys += 1

        node = descend(value, current)
        if isinstance(node, Match):
            match_keys += 1
            found.assign(key, node)
            current = node.remaining
        elif isinstance(node, Partial):
            partial_keys += 1
            found.assign(key, node)
            current = node.remaining
            break
        else:
            miss_keys += 1
            found.assign(key, None)
            break

    if match_keys == consider_keys:
        return Match(source, found, current)
    elif partial_keys or match_keys:
        return Partial(source, found, current)
    elif miss_keys:
        return Miss(source, None, current)
    else:
        assert False, 'Not reachable'


@trace
def descend_expr(expr, buffer):
    return match_params(expr, expr.params, buffer)


@trace
def repeat_match_params(source, params, buffer):
    current = buffer
    result = []

    while current:
        node = match_params(source, params, current)

        if isinstance(node, Match):
            result.append(node)
            current = node.remaining
        elif isinstance(node, Partial):
            result.append(node)
            break
        else:
            break

    return result


@trace
def descend_one_or_more(expr, buffer):
    pairs = list(expr.params)
    assert len(pairs) == 1
    index, sub_expr = pairs[0]
    assert index == 0

    found = parameters.Params()
    result = repeat_match_params(sub_expr, sub_expr.params, buffer)

    match_count = 0
    partial_count = 0
    current = None

    for i, node in enumerate(result):
        if isinstance(node, Match):
            found.assign(i, node)
            match_count += 1
            current = node.remaining
        elif isinstance(node, Partial):
            found.assign(i, node)
            partial_count += 1
            current = node.remaining
            break
        else:
            assert False, 'Should not happen'

    if match_count >= 1:
        return Match(expr, found, current)
    elif partial_count >= 1:
        return Partial(expr, found, current)
    else:
        return Miss(expr, None, buffer)


@trace
def descend_zero_or_more(expr, buffer):
    pairs = list(expr.params)
    assert len(pairs) == 1
    index, sub_expr = pairs[0]
    assert index == 0

    found = parameters.Params()
    result = repeat_match_params(sub_expr, sub_expr.params, buffer)
    current = buffer

    for i, node in enumerate(result):
        if isinstance(node, Match):
            found.assign(i, node)
            current = node.remaining
        elif isinstance(node, Partial):
            if i == 0:
                found.assign(i, node)
                return Partial(expr, found, node.remaining)
            break
        else:
            break

    return Match(expr, found, current)


@trace
def descend_optional(expr, buffer):
    node = match_params(expr, expr.params, buffer)
    if isinstance(node, Match):
        return Match(expr, node, node.remaining)
    elif isinstance(node, Partial):
        return Partial(expr, node, node.remaining)
    else:
        return Match(expr, None, buffer)


@trace
def descend_and(expr, buffer):
    node = match_params(expr, expr.params, buffer)
    if isinstance(node, Match):
        return Match(expr, node, buffer)
    elif isinstance(node, Partial):
        return Partial(expr, node, buffer)
    else:
        return Miss(expr, node, buffer)


@trace
def descend_not(expr, buffer):
    node = match_params(expr, expr.params, buffer)
    if isinstance(node, Match):
        return Miss(expr, node, buffer)
    else:
        return Match(expr, node, buffer)


def longest_reader(nodes):
    longest_index = -1
    longest_node = None

    for node in nodes:
        if node.remaining.index > longest_index:
            longest_index = node.remaining.index
            longest_node = node

    return longest_node


@trace
def descend_choice(expr, buffer):
    found = parameters.Params()
    match_node = None
    partial_nodes = []

    for key, value in expr.params:
        if match_node is None:
            node = descend(value, buffer)
            if isinstance(node, Match):
                found.assign(key, node)
                match_node = node
                continue
            elif isinstance(node, Partial):
                found.assign(key, node)
                partial_nodes.append(node)
                continue

        found.assign(key, None)

    if match_node:
        return Match(expr, found, match_node.remaining)
    elif partial_nodes:
        longest_partial = longest_reader(partial_nodes)
        return Partial(expr, found, longest_partial.remaining)
    else:
        return Miss(expr, None, buffer)


@trace
def descend_str(expr, buffer):
    value, remaining = buffer.read(len(expr))
    if expr == value.text:
        return Match(expr, value, remaining)
    else:
        return Miss(expr, None, buffer)


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


@trace
def descend(item, buffer):
    if not buffer:
        return Miss(item, None, buffer)

    print(f'Descending: {item=}, {type(item)=} with {buffer=}')
    visitor = VISITORS[type(item)]
    return visitor(item, buffer)


def pick_failure(failures):
    longest_node = longest_reader(failures)
    if longest_node.remaining.index > 0:
        raise IncompleteParseError(longest_node)
    else:
        raise NothingMatchesError(longest_node.remaining)


def parse(rules, buffer):
    failures = []

    for rule in rules:
        node = descend(rule, buffer)
        if isinstance(node, Match) and not node.remaining:
            return node
        else:
            failures.append(node)

    pick_failure(failures)

