def get_table_dimentions(first_word_index: int, last_word_index: int, words: list[dict[str, any]]) -> tuple[float, float, float, float]:
    """
    Get the dimensions of the table in the PDF page based on first and last table words coordinates
    """

    left: float = words[first_word_index]["x0"]
    right: float = words[last_word_index]["x1"] + 5
    top: float = words[first_word_index]["top"]
    bottom: float = words[last_word_index]["bottom"]

    return (top, left, bottom, right)

def get_first_table_word_index(words: list[dict[str, any]], cardFirstFourNumbers: str, cardLastFourNumbers: str) -> int:
    """
    Get the index of the first word in the table.
    """

    top_sequence = ("Card", "number", cardFirstFourNumbers, "XXXX", "XXXX", cardLastFourNumbers)
    return find_word_adjacent_to_the_sequence((top_sequence,), words)

def get_last_table_word_index(words: list[dict[str, any]], cardFirstFourNumbers: str):
    """
    Get the index of the last word in the table.
    """

    bottom_sequence_1 = ("Page", "_", "of")
    bottom_sequence_2 = ("Total", "for", cardFirstFourNumbers)
    return find_word_adjacent_to_the_sequence((bottom_sequence_1, bottom_sequence_2), words, adjacent_left=True)

def find_word_adjacent_to_the_sequence(sequences: tuple[tuple[str, ...], ...], words: list[dict[str, any]], adjacent_left: bool=False) -> int:
    """
    Find the index of the word that is adjacent to a specific sequence of words.
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

def get_column_positions(table_coords: tuple[float, float, float, float], words: list[dict[str, any]]) -> dict[str, tuple[float, float]]:
    """
    Get the positions of the table headers in range of words based on hardcoded sequence of words.
    This function should return a dictionary with header names as keys and their positions as values.
    """

    top_sequence = ("date", "date", "Description", "Spend", "Categories", "Amount($)")
    index = find_word_adjacent_to_the_sequence((top_sequence,), words, adjacent_left=True)

    if index < 0:
        raise ValueError("Table headers were not found.")
    
    post_date_start: float = words[index + 2]["x0"] - 10
    description_start: float = words[index + 3]["x0"] - 10
    category_start: float = words[index + 4]["x0"] - 10
    amount_start: float = words[index + 6]["x0"] - 10

    return {
        "transaction_date": (table_coords[1], post_date_start),
        "post_date": (post_date_start, description_start),
        "description": (description_start, category_start),
        "category": (category_start, amount_start),
        "amount": (amount_start, table_coords[3]),
    }