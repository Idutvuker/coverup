

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

