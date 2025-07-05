import pandas as pd
import pdfplumber
from collections import defaultdict


def extract_table_data(page: pdfplumber.pdf.Page, cardFirstFourNumbers: str, cardLastFourNumbers: str) -> pd.DataFrame:
    """
    Extract a table with credit card statements from a PDF page
    """

    words = page.extract_words()

    first_word_index = get_first_table_word_index(words, cardFirstFourNumbers, cardLastFourNumbers)
    last_word_index = get_last_table_word_index(words, cardFirstFourNumbers)

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

def get_table_dimentions(first_word_index: int, last_word_index: int, words: list[dict[str, any]]) -> tuple[float]:
    """
    Get the dimensions of the table in the PDF page.
    This function returns a tuple of table coordinates.
    """
  
    left = words[first_word_index]["x0"]
    right = words[last_word_index]["x1"] + 5 # +5 to include the right border of the last word
    top = words[first_word_index]["top"]
    bottom = words[last_word_index]["bottom"]

    return (top, left, bottom, right)

def get_first_table_word_index(words: list[dict[str, any]], cardFirstFourNumbers: str, cardLastFourNumbers: str) -> int:
    """
    Get the index of the first word in the table.
    """
    top_sequence = ("Card", "number", cardFirstFourNumbers, "XXXX", "XXXX", cardLastFourNumbers)  # used to find top of table

    index = find_word_adjacent_to_the_sequence((top_sequence,), words)

    return index

def get_last_table_word_index(words: list[dict[str, any]], cardFirstFourNumbers: str) -> int:
    """
    Get the index of the last word in the table.
    """
    bottom_sequence_1 = ["Page", "_", "of"]
    bottom_sequence_2 = ["Total", "for", cardFirstFourNumbers]

    index = find_word_adjacent_to_the_sequence((bottom_sequence_1, bottom_sequence_2), words, adjacent_left=True)

    return index


def find_word_adjacent_to_the_sequence(sequences: tuple[tuple[str]], words: list[dict[str, any]], adjacent_left=False) -> int:
    """
    Find the index of the word that is adjacent to a specific sequence in the list of words.
    Note. Symbool "_" indicates that the word is not important and can be skipped.
    """

    index = -1
    for sequence in sequences:
        pointer = 0
        for i in range(len(words)):
            word_text = words[i]["text"]
            if word_text == sequence[pointer] or sequence[pointer] == "_":
                pointer += 1
                if pointer == len(sequence):
                    index = i - len(sequence) if adjacent_left else i + 1
                    break
            else:
                pointer = 0

    if index >= 0 and words[index]["text"] == "Ý":
        index = index - 1 if adjacent_left else index + 1

    return index

def get_column_positions(table_coords: tuple[float], words: list[dict[str, any]]) -> dict[str, tuple[float, float]]:
    """
    Get the positions of the table headers in range of words from from first_word_index to last_word_index.
    This function should return a dictionary with header names as keys and their positions as values.
    """

    top_sequence = ("date", "date", "Description", "Spend", "Categories", "Amount($)")  # used to find top of table
    
    index = find_word_adjacent_to_the_sequence((top_sequence,), words, adjacent_left=True)

    if index < 0:
        raise ValueError("Table headers were not found.")
    
    post_date_start = words[index + 2]["x0"] - 10
    description_start = words[index + 3]["x0"] - 10
    category_start = words[index + 4]["x0"] - 10
    amount_start = words[index + 6]["x0"] - 10

    column_positions = {
        "transaction_date": (table_coords[1], post_date_start),
        "post_date": (post_date_start, description_start),
        "description": (description_start, category_start),
        "category": (category_start, amount_start),
        "amount": (amount_start, table_coords[3]),
    }
    
    return column_positions


def clean_data_frame(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the DataFrame by removing rows that are empty or contain only NaN values.
    """
    # TODO: Remove rows that are empty or contain only NaN values
    return df.reset_index(drop=True)

def process_pdf(pdf_path: str, cardFirstFourNumbers: str, cardLastFourNumbers: str) -> pd.DataFrame:
    """
    Process the PDF file and extract the table data.
    """

    frames: list[pd.DataFrame] = []
    with pdfplumber.open(pdf_path) as pdf:
        # Assuming we want to process the first page
        for page in pdf.pages[1:]:
            # Extract the table data from the page
            df = extract_table_data(page, cardFirstFourNumbers, cardLastFourNumbers)
            
            # Clean the DataFrame
            df = clean_data_frame(df)

            frames.append(df)

    full_df = pd.concat(frames, ignore_index=True)

    print(full_df)  
    return full_df


if __name__ == "__main__":
    process_pdf("data/<name_if_statement_document>.pdf", "<your_credit_card_first_4_digits>", "<your_credit_card_last_4_digits>")