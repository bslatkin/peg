from grammar import *


MY_GRAMMAR = {
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
            Ref('Sum'),
            ')')),
}


MY_LANGUAGE = Language(MY_GRAMMAR)

for rule in MY_LANGUAGE.rules.values():
    print(rule)


import parser

result = parser.parse(MY_LANGUAGE.rules.values(), '(3^5+1)*2')
print(repr(result))


import syntax

flat = syntax.coalesce(result)

breakpoint()
