"""
Main entry point for the CIBC statements parser.

This script processes PDF statement file
with one or multiple statement tables and combines the results.
"""

import pandas as pd
import pdfplumber

from table_extractor import TableExtractor


class PDFProcessor:
    """
    Responsible for processing a whole PDF file.

    Get statements data from one or more pages.
    """

    def __init__(self, card_first_four: str, card_last_four: str) -> None:
        """
        Initialize the PDFProcessor.

        Args:
            card_first_four (str): First four digits of the card number.
            card_last_four (str): Last four digits of the card number.
        """
        self.extractor = TableExtractor(card_first_four, card_last_four)

    def process_pdf(self, pdf_path: str) -> pd.DataFrame:
        """
        Process the PDF file and extract statements data.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            pd.DataFrame: DataFrame containing the extracted statement data.
        """
        frames: list[pd.DataFrame] = []
        from_page: int = 1  # statements data usually starts from page 2 (index 1)
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[from_page:]:
                df = self.extractor.extract_table_data(page)
                frames.append(df)

        return pd.concat(frames, ignore_index=True)
