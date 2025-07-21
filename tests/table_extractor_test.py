"""Unit tests for table_extractor.py."""

from typing import Any

import pandas as pd

from src.constants.table_headers import Col
from src.table_extractor import TableExtractor


class DummyPage:
    """Mock pdfplumber.page.Page for testing."""

    def extract_words(self) -> list[dict[str, Any]]:
        # Minimal mock for extraction logic
        return [
            {"text": "Trans", "x0": 36, "x1": 54, "top": 172, "bottom": 179},
            {"text": "Post", "x0": 78, "x1": 92, "top": 172, "bottom": 179},
            {"text": "date", "x0": 36, "x1": 51, "top": 180, "bottom": 187},
            {"text": "date", "x0": 78, "x1": 93, "top": 180, "bottom": 187},
            {"text": "Description", "x0": 122, "x1": 159, "top": 180, "bottom": 187},
            {"text": "Spend", "x0": 325, "x1": 346, "top": 180, "bottom": 187},
            {"text": "Categories", "x0": 348, "x1": 383, "top": 180, "bottom": 187},
            {"text": "Amount($)", "x0": 504, "x1": 540, "top": 180, "bottom": 187},
            {"text": "Card", "x0": 36, "x1": 56, "top": 191, "bottom": 200},
            {"text": "number", "x0": 58, "x1": 91, "top": 191, "bottom": 200},
            {"text": "1234", "x0": 94, "x1": 114, "top": 191, "bottom": 200},
            {"text": "XXXX", "x0": 117, "x1": 140, "top": 191, "bottom": 200},
            {"text": "XXXX", "x0": 143, "x1": 167, "top": 191, "bottom": 200},
            {"text": "5678", "x0": 169, "x1": 189, "top": 191, "bottom": 200},
            {"text": "Ý", "x0": 108, "x1": 117, "top": 203, "bottom": 213},
            {"text": "Jul", "x0": 36, "x1": 45, "top": 208, "bottom": 215},
            {"text": "24", "x0": 47, "x1": 56, "top": 208, "bottom": 215},
            {"text": "Jul", "x0": 78, "x1": 87, "top": 208, "bottom": 216},
            {"text": "26", "x0": 89, "x1": 98, "top": 208, "bottom": 216},
            {"text": "Some", "x0": 122, "x1": 148, "top": 208, "bottom": 215},
            {"text": "Restaurant", "x0": 150, "x1": 213, "top": 208, "bottom": 215},
            {"text": "TORONTO", "x0": 219, "x1": 253, "top": 208, "bottom": 215},
            {"text": "ON", "x0": 266, "x1": 277, "top": 208, "bottom": 215},
            {"text": "Restaurants", "x0": 341, "x1": 390, "top": 208, "bottom": 215},
            {"text": "73.66", "x0": 524, "x1": 539, "top": 208, "bottom": 215},
            {"text": "Page", "x0": 481, "x1": 500, "top": 513, "bottom": 522},
            {"text": "2", "x0": 503, "x1": 508, "top": 513, "bottom": 522},
            {"text": "of", "x0": 510, "x1": 518, "top": 513, "bottom": 522},
            {"text": "4", "x0": 521, "x1": 526, "top": 513, "bottom": 522},
        ]


def test_extract_table_data_returns_dataframe() -> None:
    extractor = TableExtractor("1234", "5678")
    page = DummyPage()
    df = extractor.extract_table_data(page)
    assert isinstance(df, pd.DataFrame)

    expected_columns = [
        Col.TRANS_DATE,
        Col.POST_DATE,
        Col.DESCRIPTION,
        Col.CATEGORY,
        Col.AMOUNT,
    ]
    assert (
        df.columns.tolist() == expected_columns
    ), f"Columns mismatch: {df.columns.tolist()}"

    expected_rows_count = 1
    assert (
        len(df.values) == expected_rows_count
    ), f"Length should be {expected_rows_count}"
