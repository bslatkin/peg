import parameters



class Ref:
    def __init__(self, symbol):
        self.symbol = symbol

    def __repr__(self):
        return f'{self.__class__.__name__}({self.symbol!r})'


class Expr:
    def __init__(self, *items, **mappings):
        if items:
            assert not mappings
            self.params = parameters.Params.from_list(*items)
        elif mappings:
            assert not items
            self.params = parameters.Params.from_dict(**mappings)
        else:
            assert False, 'Must have an item or mapping present'

    def __repr__(self):
        repr_string = parameters.repr_params(self.params)
        return f'{self.__class__.__name__}({repr_string})'


class Choice(Expr):
    pass


class RepeatedExpr(Expr):
    def __init__(self, *args, **kwargs):
        super().__init__(Expr(*args, **kwargs))


class ZeroOrMore(RepeatedExpr):
    pass


class OneOrMore(RepeatedExpr):
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
        return (
            f'{self.__class__.__name__}'
            f'({self.symbol!r}, {self.expr!r})')


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

    derefed_params = parameters.Params()

    for key, other_value in value.params:
        derefed = deref_single(rules, other_value)
        derefed_params.assign(key, derefed)

    value.params = derefed_params

    return value


def resolve_refs(grammar):
    rules = {}

    for symbol, value in grammar.items():
        assert isinstance(symbol, str)

        dereferenced = deref_single(rules, value)
        rule = get_rule(rules, symbol)
        rule.expr = dereferenced

    return rules.values()
