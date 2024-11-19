from typing import List


def smart_split(text, max_line_length=120) -> List[str]:
	"""
	Splits a string into lines, trying to keep words intact and within the
	specified max_line_length.

	Args:
	  text: The string to split.
	  max_line_length: The maximum length of each line.

	Returns:
	  A list of strings, where each string is a line.
	"""

	words = text.split()
	lines = []
	current_line = []

	current_line_length: int = 0

	for word in words:
		if current_line_length + len(word) <= max_line_length:
			current_line.append(word)
			current_line_length += len(word) + 1
		else:
			lines.append(" ".join(current_line))
			current_line = [word + " "]
			current_line_length = len(word) + 1

	if current_line:
		lines.append(" ".join(current_line))

	return lines