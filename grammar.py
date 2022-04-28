
class Ref:
	def __init__(self, symbol):
		self.symbol = symbol

	def __repr__(self):
		return f'{self.__class__.__name__}({self.symbol!r})'


def repr_items(items):
	pieces = []
	for item in items:
		if isinstance(item, Rule):
			pieces.append(f'{item.__class__.__name__}({item.symbol!r}, ...)')
		else:
			pieces.append(repr(item))

	return ', '.join(pieces)


class Expr:
	def __init__(self, *items):
		self.items = items

	def __repr__(self):
		items_string = repr_items(self.items)
		return f'{self.__class__.__name__}({items_string})'



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
		items_string = repr_items([self.expr])
		return (
			f'{self.__class__.__name__}'
			f'({self.symbol!r}, {items_string})')


def get_rule(rules, symbol):
	try:
		return rules[symbol]
	except KeyError:
		rule = Rule(symbol, None)
		rules[symbol] = rule
		return rule


def deref_item(rules, item):
	if isinstance(item, Ref):
		return get_rule(rules, item.symbol)

	if isinstance(item, str):
		return item

	assert isinstance(item, Expr)

	dereferenced = [deref_item(rules, i) for i in item.items]
	item.items = dereferenced
	return item


def substitute_refs(grammar):
	rules = {}

	for symbol, item in grammar.items():
		assert isinstance(symbol, str)

		dereferenced = deref_item(rules, item)
		rule = get_rule(rules, symbol)
		rule.expr = dereferenced

	return rules


class Language:
	def __init__(self, grammar):
		self.rules = substitute_refs(grammar)
