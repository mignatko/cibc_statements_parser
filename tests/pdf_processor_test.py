"""Unit tests for pdf_processor.py."""

from types import TracebackType
from typing import Self

import pandas as pd
import pytest

from src.pdf_processor import UNKNOWN, PDFProcessor
from src.table_headers import Col


class DummyPage:
    def extract_words(self) -> list:
        return []

    def search(self, pattern: str) -> list[dict[str, list[str]]]:
        # Simulate a match for "Statement Date"
        if "Statement" in pattern:
            return [{"groups": ["Jan 15, 2024"]}]
        return []


class DummyPDF:
    def __init__(self, *, with_pages: bool = True) -> None:
        # At least two pages: first for cover, second for statement
        self.pages = [DummyPage(), DummyPage()] if with_pages else []

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass


class DummyExtractor:
    def extract_table_data(self, _page: DummyPage) -> pd.DataFrame:
        # Return a simple DataFrame for testing
        return pd.DataFrame(
            {
                Col.TRANS_DATE: ["Jan 1"],
                Col.POST_DATE: ["Jan 2"],
                Col.DESCRIPTION: ["STORE CITY ON"],
                Col.CATEGORY: ["Groceries"],
                Col.AMOUNT: [-12.34],
            },
        )


@pytest.fixture
def processor(monkeypatch: pytest.MonkeyPatch) -> PDFProcessor:
    proc = PDFProcessor("1234", "5678")
    proc.extractor = DummyExtractor()
    monkeypatch.setattr("src.pdf_processor.pdfplumber.open", lambda _: DummyPDF())
    return proc


def test_process_pdf_returns_dataframe(processor: PDFProcessor) -> None:
    df = processor.process_pdf("dummy.pdf")
    assert isinstance(df, pd.DataFrame)
    assert Col.TRANS_DATE.value in df.columns


def test_get_year_from_first_page_found(monkeypatch: pytest.MonkeyPatch) -> None:
    proc = PDFProcessor("1234", "5678")
    monkeypatch.setattr("src.pdf_processor.pdfplumber.open", lambda _: DummyPDF())
    year = proc.get_year_from_first_page("dummy.pdf")
    assert year == "2024"


def test_get_year_from_first_page_no_pages(monkeypatch: pytest.MonkeyPatch) -> None:
    proc = PDFProcessor("1234", "5678")
    monkeypatch.setattr(
        "src.pdf_processor.pdfplumber.open",
        lambda _: DummyPDF(with_pages=False),
    )
    year = proc.get_year_from_first_page("dummy.pdf")
    assert year == "2000"


def test_process_dataframe_and_description_full() -> None:
    proc = PDFProcessor("1234", "5678")
    # DataFrame with all required columns
    df = pd.DataFrame(
        {
            Col.TRANS_DATE: ["Jan 1"],
            Col.POST_DATE: ["Jan 2"],
            Col.DESCRIPTION: ["WALMART TORONTO ON"],
            Col.CATEGORY: ["Groceries"],
            Col.AMOUNT: [-12.34],  # float, not string!
        },
    )

    result = proc.process_dataframe(df, "2024")
    assert pd.api.types.is_datetime64_any_dtype(result[Col.TRANS_DATE])
    assert pd.api.types.is_datetime64_any_dtype(result[Col.POST_DATE])
    assert "province" in result.columns
    assert "city" in result.columns
    assert "store_name" in result.columns


def test_process_dataframe_empty() -> None:
    proc = PDFProcessor("1234", "5678")
    df = pd.DataFrame()
    result = proc.process_dataframe(df, "2024")
    assert result.empty


def test_process_dataframe_description_empty() -> None:
    proc = PDFProcessor("1234", "5678")
    df = pd.DataFrame()
    result = proc.process_dataframe_description(df)
    assert result.empty


def test_process_dataframe_description_various_cases() -> None:
    proc = PDFProcessor("1234", "5678")
    # Description with @, negative amount, and Prime Member
    df = pd.DataFrame(
        {
            Col.DESCRIPTION: ["@SOMETHING", "Prime Member", "WALMART TORONTO ON"],
            Col.AMOUNT: [-10.0, 20.0, 30.0],  # float, not string!
            Col.TRANS_DATE: ["Jan 1", "Jan 2", "Jan 3"],
            Col.POST_DATE: ["Jan 1", "Jan 2", "Jan 3"],
            Col.CATEGORY: ["Cat", "Cat", "Cat"],
        },
    )

    result = proc.process_dataframe_description(df)
    assert all(col in result.columns for col in ["province", "city", "store_name"])
    # Check UNKNOWN assignment
    assert result.loc[0, "province"] == UNKNOWN
    assert result.loc[1, "province"] == UNKNOWN
