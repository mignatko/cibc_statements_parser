from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.pdf_processor import PDFProcessor


class DummyExtractor:
    def extract_table_data(self) -> pd.DataFrame:
        # Return a simple DataFrame for testing
        return pd.DataFrame({"transaction_date": ["Jan 1"], "post_date": ["Jan 2"]})


@pytest.fixture
def dummy_pdf() -> MagicMock:
    # Set up a mock PDF object with mock pages
    page0 = MagicMock()
    page0.search.return_value = [{"groups": ["Jan 15, 2023"]}]
    page1 = MagicMock()
    pdf_mock = MagicMock()
    pdf_mock.pages = [page0, page1]
    return pdf_mock


def test_pdf_processor_process_pdf(dummy_pdf: MagicMock) -> None:
    processor = PDFProcessor("1234", "5678")
    processor.extractor = DummyExtractor()

    # Patch pdfplumber.open to return our dummy_pdf context manager
    mock_open = MagicMock()
    mock_open.__enter__.return_value = dummy_pdf
    mock_open.__exit__.return_value = None

    with patch("src.pdf_processor.pdfplumber.open", return_value=mock_open):
        df = processor.process_pdf("any.pdf")
        assert isinstance(df, pd.DataFrame)
        assert "transaction_date" in df.columns
        assert pd.api.types.is_datetime64_any_dtype(df["transaction_date"])
        assert pd.api.types.is_datetime64_any_dtype(df["post_date"])

        expected_year = 2023
        assert df["transaction_date"].dt.year.iloc[0] == expected_year


def test_pdf_processor_no_statement_date() -> None:
    processor = PDFProcessor("1234", "5678")
    processor.extractor = DummyExtractor()

    # Simulate no statement date match (default year used)
    page0 = MagicMock()
    page0.search.return_value = []
    page1 = MagicMock()
    pdf_mock = MagicMock()
    pdf_mock.pages = [page0, page1]
    mock_open = MagicMock()
    mock_open.__enter__.return_value = pdf_mock
    mock_open.__exit__.return_value = None

    with patch("src.pdf_processor.pdfplumber.open", return_value=mock_open):
        df = processor.process_pdf("any.pdf")
        assert isinstance(df, pd.DataFrame)
        expected_default_year = 2000
        assert df["transaction_date"].dt.year.iloc[0] == expected_default_year
