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



# Syntax errors

def validate_sum(params):
    assert params.left is not None

    if params.suffix is None:
        return

    for term in params.suffix:
        assert term.operator is not None

        if term.right is None:
            raise syntax.ValidationError(
                'Right side term in add or subtract operation is missing',
                term)


def validate_product(params):
    assert params.left is not None

    if params.suffix is None:
        return

    for term in params.suffix:
        assert term.operator is not None

        if term.right is None:
            raise syntax.ValidationError(
                'Right side term in multiply or divide operation is missing',
                term)


def validate_power(params):
    assert params.base is not None

    if params.suffix is not None:
        assert params.suffix.operator is not None

        if params.suffix.exponent is None:
            raise syntax.ValidationError(
                'Value for exponent is missing',
                params.suffix)


def validate_value(params):
    assert (params.digits is not None) ^ (params.sub_expr is not None)

    if params.sub_expr is not None:
        assert params.sub_expr.left_paren is not None

        if params.sub_expr.inner_sum is None:
            raise syntax.ValidationError(
                'Value inside subexpression is missing',
                params.sub_expr)

        if params.sub_expr.right_parent is None:
            raise syntax.ValidationError(
                'Closing parenthesis for subexpression is missing',
                params.sub_expr)


def validate_number(params):
    assert params
    assert any(params)


ERROR_HANDLERS = {
    'Sum': validate_sum,
    'Product': validate_product,
    'Power': validate_power,
    'Value': validate_value,
    'Number': validate_number,
}



import reader


buffer = reader.get_string_reader('(1+')
# buffer = reader.get_string_reader('asdf')


import parser
import syntax

try:
    result = parser.parse(MY_RULES, buffer)
    print(repr(result))
except parser.IncompleteParseError as e:
    flat = syntax.coalesce(e.node)
    try:
        syntax.validate(ERROR_HANDLERS, flat)
    except syntax.ValidationError as e:
        breakpoint()
        print(e)
except parser.NothingMatchesError as e:
    breakpoint()
    print(e)
except Exception as e:
    # TODO: Parser bug
    raise


import reader

flat = syntax.coalesce(result)
print(repr(flat))


# Interpreter

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
    assert isinstance(digit, reader.Value)
    assert len(digit.text) == 1
    return digit.text


INTEPRET_HANDLERS = {
    'Sum': handle_sum,
    'Product': handle_product,
    'Power': handle_power,
    'Value': handle_value,
    'Number': handle_number,
}


import interpreter

context = interpreter.Context(INTEPRET_HANDLERS)
result = context.interpret(flat)
print(result)


interpreter.repl(MY_RULES, context)
