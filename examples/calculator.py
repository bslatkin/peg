import grammar
from grammar import Ref, Expr, Choice, ZeroOrMore, OneOrMore, Optional, And, Not



MY_GRAMMAR = {
    'Sum': Expr(
        left=Ref('Product'),
        suffix=ZeroOrMore(
            operator=Choice('+', '-'),
            right=Ref('Product'))),

    'Product': Expr(
        left=Ref('Power'),
        suffix=ZeroOrMore(
            operator=Choice('*', '/'),
            right=Ref('Power'))),

    'Power': Expr(
        base=Ref('Value'),
        suffix=Optional(
            operator='^',
            exponent=Ref('Power'))),

    'Value': Choice(
        digits=OneOrMore(Ref('Number')),
        sub_expr=Expr(
            left_paren='(',
            inner_sum=Ref('Sum'),
            right_paren=')')),

    'Number': Choice('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'),
}


MY_RULES = grammar.resolve_refs(MY_GRAMMAR)


import reader

buffer = reader.get_string_reader('(1+2)^3')


import parser

root = parser.parse(MY_RULES, buffer)


def handle_sum(context, value):
    left = context.interpret(value.left)

    if not value.suffix:
        return left

    accumulator = left

    for suffix in value.suffix:
        operator = suffix.operator[0]
        right = context.interpret(suffix.right)

        if operator.text == '+':
            accumulator += right
        elif operator.text == '-':
            accumulator -= right
        else:
            assert False, 'Bad operator'

    return accumulator


def handle_product(context, value):
    left = context.interpret(value.left)

    if not value.suffix:
        return left

    raise NotImplementedError


def handle_power(context, value):
    base = context.interpret(value.base)

    if not value.suffix:
        return base

    exponent = context.interpret(value.suffix.exponent)

    return base ** exponent


def handle_value(context, value):
    if value.digits:
        return int(value.digits.text)

    assert value.sub_expr

    return context.interpret(value.sub_expr.inner_sum)


INTEPRET_HANDLERS = {
    'Sum': handle_sum,
    'Product': handle_product,
    'Power': handle_power,
    'Value': handle_value,
}


import interpreter

# XXX: Need to test exponents and optional, it's not working

context = interpreter.Context(INTEPRET_HANDLERS)
result = context.interpret(root)
print(result)


# interpreter.repl(MY_RULES, context)
