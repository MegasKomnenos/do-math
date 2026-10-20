"""S1: the public Python boundary shared by the provider and consumer."""

from typing import Protocol, TypeAlias

LineCounts: TypeAlias = dict[str, int]
IMPLEMENTATION_MODULE = "linecount.core"
IMPLEMENTATION_SYMBOL = "count_lines"


class LineCounter(Protocol):
    def __call__(self, text: str) -> LineCounts:
        """Accept text positionally or as text=; return the counts dictionary itself."""
        ...
