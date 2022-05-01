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

result = parser.parse(MY_LANGUAGE.rules.values(), '(21+35)')
print(repr(result))

# breakpoint()


import syntax

flat = syntax.coalesce(result)
print(repr(flat))

breakpoint()


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
    if not isinstance(node.value, list):
        return context.interpret(node.value)

    # TODO: This is really ugly that I have to reengineer how the parser
    # matched I'm coming back to interpret the results, when I knew full well
    # what was happening at parse time. Instead, I should name each piece of
    # the rule and then pull that through all the way to the end so it can be
    # used here.

    assert len(node.value) > 0

    if node.value[0] == '(':
        assert len(node.value) == 3
        assert node.value[0] == '('
        assert node.value[2] == ')'
        return context.interpret(node.value[1])

    else:
        return int(''.join(context.interpret(v) for v in node.value))


def handle_number(context, node):
    assert isinstance(node.value, str)
    return node.value


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
