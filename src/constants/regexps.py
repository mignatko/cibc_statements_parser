"""
Regular expression patterns for the CIBC Statements Parser.

Contains compiled regex patterns for parsing and extracting statement data.
"""

import re
from typing import Final

ASCII_WORD_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z]+$")
STORE_NAME_RE: Final[re.Pattern[str]] = re.compile(r"^([^\d#,*/,/]+)")
STATEMENT_DATE_RE: Final[re.Pattern[str]] = re.compile(
    r"Statement\s+Date\s*([\s\S]+?)\n",
)
