"""
Canadian province abbreviations for the CIBC Statements Parser.

Defines a set of valid province codes used for location extraction.
"""

from typing import Final

PROVINCES: Final[frozenset[str]] = frozenset(
    ["AB", "BC", "MB", "NB", "NL", "NS", "NT", "NU", "ON", "PE", "QC", "SK", "YT"],
)
