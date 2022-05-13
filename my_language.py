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

for rule in MY_RULES:
    print(rule)

# breakpoint()


import reader

buffer = reader.get_string_reader('(21+35+17+8)^')


import parser

result = parser.parse(MY_RULES, buffer)
print(repr(result))

breakpoint()


import syntax

flat = syntax.coalesce(result)
print(repr(flat))

# breakpoint()


def handle_sum(context, value):
    left = context.interpret(value.left)

    if not value.suffix:
        return left

    accumulator = left

    for suffix in value.suffix:
        operator = suffix.operator[0]
        right = context.interpret(suffix.right)

        if operator == '+':
            accumulator += right
        elif operator == '-':
            accumulator -= right
        else:
            assert False, 'Bad operator'

    return accumulator


def handle_product(context, value):
    left = context.interpret(value.left)

    if value.suffix is None:
        return left

    raise NotImplementedError


def handle_power(context, value):
    base = context.interpret(value.base)

    if value.suffix is None:
        return base

    exponent = context.interpret(value.suffix.exponent)

    return base ** exponent


def handle_value(context, value):
    if value.digits is not None:
        return int(''.join(context.interpret(d[0]) for d in value.digits))

    assert value.sub_expr

    return context.interpret(value.sub_expr.inner_sum)


def handle_number(context, value):
    digit = value[0]
    assert isinstance(digit, str)
    assert len(digit) == 1
    return digit


MY_HANDLERS = {
    'Sum': handle_sum,
    'Product': handle_product,
    'Power': handle_power,
    'Value': handle_value,
    'Number': handle_number,
}


import interpreter

context = interpreter.Context(MY_HANDLERS)
result = context.interpret(flat)
print(result)


interpreter.repl(MY_RULES, context)
