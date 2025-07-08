"""PDF processing module for extracting statement tables from CIBC PDFs."""

from collections import defaultdict
from typing import Any

import pandas as pd
from pdfplumber.page import Page

from utils import (
    get_column_positions,
    get_first_table_word_index,
    get_last_table_word_index,
    get_table_dimentions,
)


class TableExtractor:
    """Responsible for extraction data from a PDF, convertion it to ``pd.DataFrame``."""

    def __init__(self, card_first_digits: str, card_last_digits: str) -> None:
        """
        Initialize a TableExtractor with first and last 4 card digits.

        Args:
            card_first_digits (str): The first 4 digits of the credit card.
            card_last_digits (str): The last 4 digits of the credit card.
        """
        self.card_first_digits = card_first_digits
        self.card_last_digits = card_last_digits

    def extract_table_data(self, page: Page) -> pd.DataFrame:
        """
        Extract a table with credit card statements from a PDF page.

        Args:
            page (pdfplumber.pdf.Page): The PDF page to extract data from.

        Returns:
            A ``pandas.DataFrame`` containing the extracted table data.
            An empty DataFrame is returned if extraction fails.
        """
        words: list[dict[str, Any]] = page.extract_words()
        first_word_index = get_first_table_word_index(
            words,
            self.card_first_digits,
            self.card_last_digits,
        )
        last_word_index = get_last_table_word_index(words, self.card_first_digits)

        if first_word_index < 0 or last_word_index < 0:
            return pd.DataFrame()

        table_coords = get_table_dimentions(first_word_index, last_word_index, words)
        column_positions = get_column_positions(table_coords, words)

        # TODO @mignatko: move to a private method
        rows: defaultdict[int, defaultdict[str, str]] = defaultdict(
            lambda: defaultdict(str),
        )
        current_row = int(words[0]["top"])
        for i in range(first_word_index, last_word_index + 1):
            if words[i]["text"] == "Ý":
                continue

            for key, (start, end) in column_positions.items():
                if abs(int(words[i]["top"]) - current_row) <= 1:
                    if words[i]["x0"] > start and words[i]["x1"] <= end:
                        rows[current_row][key] += f"{words[i]['text']} "
                elif words[i]["x0"] > column_positions["transaction_date"][1]:
                    # TODO @mignatko: refactor:
                    # without skipping other columns we'll duplicate the same word
                    # and past to description len(columns_positions - 1) times
                    if key != "description":
                        continue
                    rows[current_row]["description"] += f"{words[i]['text']} "
                else:
                    current_row = int(words[i]["top"])
                    rows[current_row]["transaction_date"] += f"{words[i]['text']} "

        return pd.DataFrame.from_dict(rows, orient="index")
