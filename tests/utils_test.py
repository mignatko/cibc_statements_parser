"""Unit tests for utils.py."""

from typing import Any

import pytest

from src.constants.table_headers import Col
from src.utils import (
    find_word_adjacent_to_the_sequence,
    get_column_positions,
    get_first_table_word_index,
    get_last_table_word_index,
    get_table_dimentions,
)


@pytest.fixture
def sample_words() -> list[dict[str, Any]]:
    return [
        {"text": "Trans", "x0": 61, "x1": 70, "top": 0, "bottom": 10},
        {"text": "Post", "x0": 71, "x1": 80, "top": 0, "bottom": 10},
        {"text": "date", "x0": 61, "x1": 70, "top": 20, "bottom": 30},
        {"text": "date", "x0": 71, "x1": 80, "top": 20, "bottom": 30},
        {"text": "Description", "x0": 81, "x1": 100, "top": 20, "bottom": 30},
        {"text": "Spend", "x0": 101, "x1": 110, "top": 20, "bottom": 30},
        {"text": "Categories", "x0": 111, "x1": 120, "top": 20, "bottom": 30},
        {"text": "Amount($)", "x0": 121, "x1": 130, "top": 0, "bottom": 10},
        {"text": "Card", "x0": 0, "x1": 10, "top": 0, "bottom": 10},
        {"text": "number", "x0": 11, "x1": 20, "top": 0, "bottom": 10},
        {"text": "1234", "x0": 21, "x1": 30, "top": 0, "bottom": 10},
        {"text": "XXXX", "x0": 31, "x1": 40, "top": 0, "bottom": 10},
        {"text": "XXXX", "x0": 41, "x1": 50, "top": 0, "bottom": 10},
        {"text": "5678", "x0": 51, "x1": 60, "top": 0, "bottom": 10},
        {"text": "Page", "x0": 131, "x1": 140, "top": 0, "bottom": 10},
        {"text": "1", "x0": 141, "x1": 150, "top": 0, "bottom": 10},
        {"text": "of", "x0": 151, "x1": 160, "top": 0, "bottom": 10},
        {"text": "Total", "x0": 161, "x1": 170, "top": 0, "bottom": 10},
        {"text": "for", "x0": 171, "x1": 180, "top": 0, "bottom": 10},
        {"text": "1234", "x0": 181, "x1": 190, "top": 0, "bottom": 10},
    ]


def test_get_table_dimentions(sample_words: list[dict[str, Any]]) -> None:
    dims = get_table_dimentions(0, 5, sample_words)
    assert isinstance(dims, tuple)
    expected_dimentions_count = 4
    assert len(dims) == expected_dimentions_count


def test_get_first_table_word_index(sample_words: list[dict[str, Any]]) -> None:
    idx = get_first_table_word_index(sample_words, "1234", "5678")
    assert idx >= 0


def test_get_last_table_word_index(sample_words: list[dict[str, Any]]) -> None:
    idx = get_last_table_word_index(sample_words, "1234")
    assert idx >= 0


def test_find_word_adjacent_to_the_sequence(sample_words: list[dict[str, Any]]) -> None:
    seq = (("Card", "number", "1234", "XXXX", "XXXX", "5678"),)
    idx = find_word_adjacent_to_the_sequence(seq, sample_words, adjacent_left=False)
    assert idx >= 0


def test_get_column_positions(sample_words: list[dict[str, Any]]) -> None:
    dims = get_table_dimentions(0, 11, sample_words)
    positions = get_column_positions(dims, sample_words)
    assert isinstance(positions, dict)
    for col in [
        Col.TRANS_DATE,
        Col.POST_DATE,
        Col.DESCRIPTION,
        Col.CATEGORY,
        Col.AMOUNT,
    ]:
        assert col in positions
