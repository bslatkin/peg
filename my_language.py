from grammar import *


# Coalesce the keyword arguments in the grammar up to each rule
# when it matches. Make sure they're not repeated or overwritten.
# Assign these values on the final object that is handed to the
# interpreter or code generator. Assign the keys to None that aren't
# assigned (or maybe a special missing value or accessor).

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


MY_LANGUAGE = Language(MY_GRAMMAR)

for rule in MY_LANGUAGE.rules.values():
    print(rule)

# breakpoint()


import parser

result = parser.parse(MY_LANGUAGE.rules.values(), '(21+35)^3')
print(repr(result))

# breakpoint()


import syntax

flat = syntax.coalesce(result)
print(repr(flat))

# breakpoint()


def handle_sum(context, node):
    left = context.interpret(node.value.left)

    if node.value.suffix is None:
        return left

    operator = node.value.suffix.operator

    right = context.interpret(node.value.suffix.right)

    if operator == '+':
        return left + right
    elif operator == '-':
        return left - right
    else:
        assert False, 'Bad operator'


def handle_product(context, node):
    left = context.interpret(node.value.left)

    if node.value.suffix is None:
        return left

    raise NotImplementedError


def handle_power(context, node):
    base = context.interpret(node.value.base)

    if node.value.suffix is None:
        return base

    exponent = context.interpret(node.value.suffix.exponent)

    return base ** exponent


def handle_value(context, node):
    if node.value.digits is not None:
        digits = []
        if isinstance(node.value.digits, list):
            digits.extend(context.interpret(d) for d in node.value.digits)
        else:
            digits.append(context.interpret(node.value.digits))

        return int(''.join(digits))

    assert node.value.sub_expr

    return context.interpret(node.value.sub_expr.inner_sum)


def handle_number(context, node):
    value = node.value.get_single_value()
    assert isinstance(value, str)
    return value


def handle_str(context, node):
    return node


MY_HANDLERS = {
    'Sum': handle_sum,
    'Product': handle_product,
    'Power': handle_power,
    'Value': handle_value,
    'Number': handle_number,
    str: handle_str,
}


import interpreter

context = interpreter.Context(MY_HANDLERS)
result = context.interpret(flat)
print(result)

breakpoint()
