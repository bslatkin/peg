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

result = parser.parse(MY_LANGUAGE.rules.values(), '(2+3)')
print(repr(result))


import syntax

flat = syntax.coalesce(result)


def handle_sum(context, node):
    if not isinstance(node.value, list):
        return context.interpret(node.value)

    assert len(node.value) == 3

    left = context.interpret(node.value[0])
    operator = node.value[1]
    right = context.interpret(node.value[2])

    assert operator in ('+', '-')

    if operator == '+':
        return left + right
    else:
        return left - right


def handle_product(context, node):
    if not isinstance(node.value, list):
        return context.interpret(node.value)

    raise NotImplementedError


def handle_power(context, node):
    if not isinstance(node.value, list):
        return context.interpret(node.value)

    raise NotImplementedError


def handle_value(context, node):
    if isinstance(node.value, str):
        return int(node.value)

    assert len(node.value) == 3
    assert node.value[0] == '('
    assert node.value[2] == ')'

    return context.interpret(node.value[1])


def handle_str(context, node):
    return node


MY_HANDLERS = {
    'Sum': handle_sum,
    'Product': handle_product,
    'Power': handle_power,
    'Value': handle_value,
    str: handle_str,
}


import interpreter

context = interpreter.Context(MY_HANDLERS)
result = context.interpret(flat)
print(result)

breakpoint()
