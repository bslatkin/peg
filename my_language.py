from grammar import *


MY_GRAMMAR = {
	'Root': Ref('Sum'),

	'Sum': Expr(
		Ref('Product'),
		ZeroOrMore(
			Choice('+', '-'),
			Ref('Product'))),

	'Product': Expr(
		Ref('Power'),
		ZeroOrMore(
			Choice('*', '/'),
			Ref('Power'))),

	'Power': Expr(
		Ref('Value'),
		Optional(
			'^',
			Ref('Power'))),

	'Value': Choice(
		OneOrMore(
			Choice('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')),
		Expr(
			'(',
			Ref('Root'),
			')')),
}


MY_LANGUAGE = Language(MY_GRAMMAR)

for rule in MY_LANGUAGE.rules.values():
	print(rule)


import parser

result = parser.parse(MY_LANGUAGE.rules.values(), '1+1')
print(repr(result))
