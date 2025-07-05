import pandas as pd
import pdfplumber
from collections import defaultdict
from utils import (
    get_first_table_word_index,
    get_last_table_word_index,
    get_table_dimentions,
    get_column_positions,
)

class TableExtractor:
    """
    Contains logic for extraction data from a PDF page and convertion it to a pandas DataFrame 
    """
    
    def __init__(self, card_first_digits: str, card_last_digits: str):
        self.card_first_digits = card_first_digits
        self.card_last_digits = card_last_digits

    def extract_table_data(self, page: pdfplumber.pdf.Page) -> pd.DataFrame:
        """
        Extract a table with credit card statements from a PDF page
        """

        words: list[dict[str, any]] = page.extract_words()
        first_word_index = get_first_table_word_index(words, self.card_first_digits, self.card_last_digits)
        last_word_index = get_last_table_word_index(words, self.card_first_digits)

        if first_word_index < 0 or last_word_index < 0:
            return pd.DataFrame()

        table_coords = get_table_dimentions(first_word_index, last_word_index, words)
        column_positions = get_column_positions(table_coords, words)

        rows = defaultdict(lambda: defaultdict(str))
        current_row = int(words[0]["top"])
        for i in range(first_word_index, last_word_index + 1):
            if words[i]["text"] == "Ý":
                continue

            for key, (start, end) in column_positions.items():
                if abs(int(words[i]["top"]) - current_row) <= 1:
                    if words[i]["x0"] > start and words[i]["x1"] <= end:
                        rows[current_row][key] += f"{words[i]['text']} "
                else:
                    if words[i]["x0"] > column_positions["transaction_date"][1]:
                        rows[current_row]["description"] += f"{words[i]['text']} "
                    else:
                        current_row = int(words[i]["top"])
                        rows[current_row]["transaction_date"] += f"{words[i]['text']} "

        df = pd.DataFrame.from_dict(rows, orient='index')
        return df