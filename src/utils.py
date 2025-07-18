"""
Utility helpers for PDF parsing.

Contains small, reusable functions used across the project.
"""

from typing import Any

from table_headers import Col


def get_table_dimentions(
    first_word_index: int,
    last_word_index: int,
    words: list[dict[str, Any]],
) -> tuple[float, float, float, float]:
    """
    Return the (top, left, bottom, right) bounds of a table.

    Args:
        first_word_index: Index of the first word belonging to the table.
        last_word_index: Index of the last word belonging to the table.
        words: Sequence returned by ``pdfplumber.Page.extract_words()``.

    Returns:
        A 4-tuple ``(top, left, bottom, right)`` in PDF point units.
    """
    left: float = words[first_word_index]["x0"]
    right: float = (
        words[last_word_index]["x1"] + 5
    )  # doesn't work for some documents without adding this extra pixels
    top: float = words[first_word_index]["top"]
    bottom: float = words[last_word_index]["bottom"]

    return (top, left, bottom, right)


def get_first_table_word_index(
    words: list[dict[str, Any]],
    card_first_four_numbers: str,
    card_last_four_numbers: str,
) -> int:
    """
    Return the index of the first word of the statement table.

    Args:
        words: Sequence returned by ``pdfplumber.Page.extract_words()``.
        card_first_four_numbers: First four digits of the card number.
        card_last_four_numbers: Last four digits of the card number.

    Returns:
        Zero-based index of the first word in the table, or ``-1`` if
        not found.
    """
    top_sequence = (
        "Card",
        "number",
        card_first_four_numbers,
        "XXXX",
        "XXXX",
        card_last_four_numbers,
    )
    return find_word_adjacent_to_the_sequence(
        (top_sequence,),
        words,
        adjacent_left=False,
    )


def get_last_table_word_index(
    words: list[dict[str, Any]],
    card_first_four_numbers: str,
) -> int:
    """
    Return the index of the last word in the statement table.

    Args:
        words: Sequence returned by ``pdfplumber.Page.extract_words()``.
        card_first_four_numbers: First four digits of the card number.

    Returns:
        Zero-based index of the last word in the table, or ``-1`` if
        not found.
    """
    bottom_sequence_1 = ("Page", "_", "of")
    bottom_sequence_2 = ("Total", "for", card_first_four_numbers)
    return find_word_adjacent_to_the_sequence(
        (bottom_sequence_1, bottom_sequence_2),
        words,
        adjacent_left=True,
    )


def find_word_adjacent_to_the_sequence(
    sequences: tuple[tuple[str, ...], ...],
    words: list[dict[str, Any]],
    *,
    adjacent_left: bool,
) -> int:
    r"""
    Return index of the word adjacent to a matching word sequence.

    The function scans ``words`` for any of the provided ``sequences``.
    The underscore ``\"_\"`` acts as a wildcard that matches any word
    and is ignored during comparison.

    Args:
        sequences: Tuple of sequences to match, e.g.
            ``(("Total", "_", "CAD"),)``.
        words: Sequence returned by ``pdfplumber.Page.extract_words()``.
        adjacent_left: If ``True`` return word immediately **left** of
            the sequence; otherwise return word immediately **right**.

    Returns:
        Index of the adjacent word, or ``-1`` if no sequence matches.
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


def get_column_positions(
    table_coords: tuple[float, float, float, float],
    words: list[dict[str, Any]],
) -> dict[str, tuple[float, float]]:
    """
    Return positions of table headers.

    Args:
        table_coords: (top, left, bottom, right) of the table rectangle.
        words: List of pdfplumber ``extract_words`` dicts.

    Returns:
        Mapping header → (x0, x1) positions.
    """
    top_sequence = (
        "date",
        "date",
        "Description",
        "Spend",
        "Categories",
        "Amount($)",
    )
    index = find_word_adjacent_to_the_sequence(
        (top_sequence,),
        words,
        adjacent_left=True,
    )

    if index < 0:
        msg = "Table headers were not found."
        raise ValueError(msg)

    post_date_start: float = words[index + 2]["x0"] - 10
    description_start: float = words[index + 3]["x0"] - 10
    category_start: float = words[index + 4]["x0"] - 10
    amount_start: float = words[index + 6]["x0"] - 10
    amount_end: float = words[index + 6]["x1"]

    return {
        Col.TRANS_DATE.value: (table_coords[1], post_date_start),
        Col.POST_DATE.value: (post_date_start, description_start),
        Col.DESCRIPTION.value: (description_start, category_start),
        Col.CATEGORY.value: (category_start, amount_start),
        Col.AMOUNT.value: (amount_start, max(table_coords[3], amount_end)),
    }
