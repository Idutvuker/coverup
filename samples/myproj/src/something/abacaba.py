

from typing import Any, Dict, Iterable, List, Mapping
import random


def reverse_string(s: str) -> str:
	"""Return a new string which is the reverse of `s`.

	Examples:
		reverse_string('abc') -> 'cba'
	"""
	if s is None:
		raise TypeError("s must be a string, got None")
	return s[::-1]


def merge_dicts(a: Mapping[str, Any], b: Mapping[str, Any]) -> Dict[str, Any]:
	"""Return a new dictionary that is a deep-ish merge of dictionaries `a` and `b`.

	Behavior:
	- Keys present only in one dict are copied.
	- If a key is present in both and both values are dict-like (Mapping),
	  the merge is applied recursively.
	- Otherwise the value from `b` overwrites the value from `a`.

	This is a small, safe merge helper (not intended to cover every edge-case
	of arbitrary mapping-like objects).
	"""
	result: Dict[str, Any] = {}
	for k, v in a.items():
		# copy initial entries from a
		result[k] = v

	for k, v in b.items():
		if k in result and isinstance(result[k], Mapping) and isinstance(v, Mapping):
			# recursive merge for nested mappings
			result[k] = merge_dicts(result[k], v)  # type: ignore[arg-type]
		else:
			result[k] = v

	return result


def roll_dice(sides: int = 6, rolls: int = 1) -> List[int]:
	"""Roll `rolls` dice with `sides` sides and return a list of integers.

	Each die returns a value in the inclusive range [1, sides]. Both `sides`
	and `rolls` must be positive integers.
	"""
	if not isinstance(sides, int) or sides < 1:
		raise ValueError("sides must be a positive integer")
	if not isinstance(rolls, int) or rolls < 1:
		raise ValueError("rolls must be a positive integer")

	return [random.randint(1, sides) for _ in range(rolls)]

