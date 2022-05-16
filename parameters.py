

def repr_params(params):
    pieces = []

    for key, value in params:
        if isinstance(key, int):
            prefix = ''
        else:
            prefix = f'{key}='

        if (not isinstance(value, Params) and
                hasattr(value, 'symbol')):
            if value.symbol is None:
                breakpoint()  # XXX
            # Prevent infinite cycles
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
