
class Ref:
    def __init__(self, symbol):
        self.symbol = symbol

    def __repr__(self):
        return f'{self.__class__.__name__}({self.symbol!r})'


# TODO: Move this and Params to a separate module
def repr_params(params):
    pieces = []

    for key, value in params:
        if isinstance(key, int):
            prefix = ''
        else:
            prefix = f'{key}='

        if isinstance(value, Rule):
            pieces.append(
                f'{prefix}{value.__class__.__name__}'
                f'({value.symbol!r}, ...)')
        else:
            pieces.append(f'{prefix}{value!r}')

    return ', '.join(pieces)


class Params:
    def __init__(self):
        self.mappings = {}

    @classmethod
    def from_list(cls, *items):
        params = cls()
        for index, value in enumerate(items):
            params.assign(index, value)
        return params

    @classmethod
    def from_dict(cls, **mappings):
        params = cls()
        for key, value in mappings.items():
            params.assign(key, value)
        return params

    def __iter__(self):
        for key, value in self.mappings.items():
            yield key, value

    def __bool__(self):
        return bool(self.mappings)

    def assign(self, key, value):
        assert key not in self.mappings
        self.mappings[key] = value

    def __repr__(self):
        repr_string = repr_params(self)
        return f'{self.__class__.__name__}({repr_string})'

    def __getitem__(self, index):
        assert isinstance(index, int)
        for i, (_, value) in enumerate(self):
            if i == index:
                return value

        raise IndexError(index)

    def __getattr__(self, key):
        return self.mappings.get(key)


class Expr:
    def __init__(self, *items, **mappings):
        if items:
            assert not mappings
            self.params = Params.from_list(*items)
        elif mappings:
            assert not items
            self.params = Params.from_dict(**mappings)
        else:
            assert False, 'Must have an item or mapping present'

    def __repr__(self):
        repr_string = repr_params(self.params)
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

    derefed_params = Params()

    for key, other_value in value.params:
        derefed = deref_single(rules, other_value)
        derefed_params.assign(key, derefed)

    value.params = derefed_params

    return value


def substitute_refs(grammar):
    rules = {}

    for symbol, value in grammar.items():
        assert isinstance(symbol, str)

        dereferenced = deref_single(rules, value)
        rule = get_rule(rules, symbol)
        rule.expr = dereferenced

    return rules


class Language:
    def __init__(self, grammar):
        self.rules = substitute_refs(grammar)
