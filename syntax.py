import parser



class SyntaxNode:
	def __init__(self, rule, value):
		self.rule = rule
		self.value = value

	def __repr__(self):
		return (
			f'{self.rule.symbol}('
			f'{self.value!r})')


def coalesce_value(value):
	result = []

	for layered in value:
		flattened = coalesce(layered)
		if flattened is None:
			continue
		elif isinstance(flattened, list):
			result.extend(flattened)
		else:
			result.append(flattened)

	if not result:
		return None

	if len(result) == 1:
		return result[0]

	return result


def coalesce(node):
	if node is None:
		return None
	elif isinstance(node, parser.RuleNode):
		flattened = coalesce(node.value)
		return SyntaxNode(node.rule, flattened)
	elif isinstance(node, list):
		return coalesce_value(node)
	elif isinstance(node, str):
		return node
	else:
		return coalesce(node.value)
