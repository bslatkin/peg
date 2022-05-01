
class Ref:
    def __init__(self, symbol):
        self.symbol = symbol

    def __repr__(self):
        return f'{self.__class__.__name__}({self.symbol!r})'


def repr_expr(items, mappings):
    pieces = []

    for item in items:
        if isinstance(item, Rule):
            pieces.append(f'{item.__class__.__name__}({item.symbol!r}, ...)')
        else:
            pieces.append(f'{item!r}')

    for key, value in mappings.items():
        if isinstance(value, Rule):
            pieces.append(
                f'{key}={value.__class__.__name__}'
                f'({value.symbol!r}, ...)')
        else:
            pieces.append(f'{key}={value!r}')

    return ', '.join(pieces)


class Expr:
    def __init__(self, *items, **mappings):
        if items:
            assert not mappings

        if mappings:
            assert not items

        self.items = items
        self.mappings = mappings


    def __repr__(self):
        repr_string = repr_expr(self.items, self.mappings)
        return f'{self.__class__.__name__}({repr_string})'



class Choice(Expr):
    pass


class ZeroOrMore(Expr):
    pass


class OneOrMore(Expr):
    pass


class Optional(Expr):
    pass


class And(Expr):
    pass


class Not(Expr):
    pass


class Rule:
    def __init__(self, symbol, expr):
        self.symbol = symbol
        self.expr = expr

    def __repr__(self):
        repr_string = repr_expr(self.expr.items, self.expr.mappings)
        return (
            f'{self.__class__.__name__}'
            f'({self.symbol!r}, {repr_string})')


def get_rule(rules, symbol):
    try:
        return rules[symbol]
    except KeyError:
        rule = Rule(symbol, None)
        rules[symbol] = rule
        return rule


def deref_single(rules, value):
    if isinstance(value, Ref):
        return get_rule(rules, value.symbol)

    if isinstance(value, str):
        return value

    assert isinstance(value, Expr)

    dereferenced_items = [deref_single(rules, i) for i in value.items]

    dereferenced_mappings = {}
    for key, other_value in value.mappings.items():
        derefered_value = deref_single(rules, other_value)
        dereferenced_mappings[key] = derefered_value

    value.items = dereferenced_items
    value.mappings = dereferenced_mappings

    return value


def substitute_refs(grammar):
    rules = {}

    for symbol, value in grammar.items():
        assert isinstance(symbol, str)

        dereferenced = deref_single(rules, value)
        rule = get_rule(rules, symbol)
        rule.expr = dereferenced

    return rules


def count_keywords(counts, value):
    if not isinstance(value, Expr):
        return

    for key, other_value in value.mappings.items():
        try:
            counts[key] += 1
        except KeyError:
            counts[key] = 1

        count_keywords(counts, other_value)


def validate_rules(rules):
    for rule in rules:
        counts = {}
        count_keywords(counts, rule.expr)
        for key, value in counts.items():
            assert value == 1, key


class Language:
    def __init__(self, grammar):
        self.rules = substitute_refs(grammar)
        validate_rules(self.rules.values())
