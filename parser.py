import re



class Node:
	def __init__(self, value, remaining):
		self.value = value
		self.remaining = remaining


class StrNode(Node):
	pass


class ExprNode(Node):
	pass


class OneOrMoreNode(Node):
	pass


class ZeroOrMoreNode(Node):
	pass


class OptionalNode(Node):
	pass


class AndNode(Node):
	pass


class NotNode(Node):
	pass


class RuleNode(Node):
	pass


def parse(rules, buffer):
	for rule in rules:
		node = descend(rule, buffer)
		if node is not None:
			return node

	return None


VISITORS = {
	And: descend_and,
	Choice: descend_choice,
	Expr: descend_expr,
	Not: descend_not,
	OneOrMore: descend_one_or_more,
	Optional: descend_optional,
	Rule: descend_rule,
	str: descend_str,
	ZeroOrMore: descend_zero_or_more,
}


def descend(item, buffer):
	visitor = VISITORS[type(item)]
	return visitor(item, buffer)


def descend_rule(rule, buffer):
	node = descend(rule.expr, buffer)
	if node is None:
		return None

	return RuleNode(rule, buffer)


def descend_expr(expr, buffer):
	found = []
	current = buffer
	for item in expr.items:
		node = descend(item, curent)
		if node is None:
			return None

		found.append(node)
		current = node.remaining

	if current:
		# Not all input was consumed so it doesn't match
		return None

	return ExprNode(found, current)


def match_items(item, buffer):
	found = []
	current = buffer
	for item in expr.items:
		node = descend(item, curent)
		if node is None:
			return None

		found.append(node)
		current = node.remaining

	if current:
		# Not all input was consumed so it doesn't match
		return None

	return ExprNode(found, current)


def repeat_match_items(items, buffer):
	found = []
	current = buffer
	while True:
		node = descend_items(items, buffer)  # XXX
		if node is None:
			break

		found.append(node)
		current = node.remaining

	return found, current


def descend_one_or_more(expr, buffer):
	found, remaining = repeat_match_items(expr.items, buffer)

	if not found:
		return None

	return OneOrMoreNode(found, remaining)


def descend_zero_or_more(expr, buffer):
	found, remaining = repeat_match_items(expr.items, buffer)
	return ZeroOrMoreNode(found, remaining)


def descend_optional(expr, buffer):
	node = descend_items(expr.items, buffer)
	if node is not None:
		return node

	return OptionalNode(None, buffer)


def descend_and(expr, buffer):
	node = descend_items(expr.items, buffer)
	if not node:
		return None

	return AndNode(node, buffer)


def descend_not(expr, buffer):
	node = descend_items(expr.items, buffer)
	if node is not None:
		return None

	return NotNode(None, buffer)


def descend_choice(expr, buffer):
	for item in expr.items:
		node = descend(item, buffer)
		if node is not None:
			return node

	return None


def descend_str(expr, buffer):
	expr_length = len(expr)
	if expr_length > len(buffer):
		return None

	for i in range(expr_length):
		if expr[i] != buffer[i]:
			return None

	consumed = buffer[:expr_length]
	remaining = buffer[expr_length:]
	return StrNode(consumed, remaining)

