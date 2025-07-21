"""
Main entry point for the CIBC statements parser.

This script processes PDF statement file
with one or multiple statement tables and combines the results.
"""

import numpy as np
import pandas as pd
import pdfplumber

from constants.keywords import UNKNOWN
from constants.provinces import PROVINCES
from constants.regexps import ASCII_WORD_RE, STATEMENT_DATE_RE, STORE_NAME_RE
from constants.table_headers import Col
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

    def get_year_from_first_page(self, pdf_path: str) -> str:
        """
        Extract the year from the first page of the PDF.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            str: Year extracted from the first page.
        """
        # TODO @mignatko: get default year from command line args
        year = "2000"  # default year
        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return year

            if pdf.pages[0] is not None:
                matches = pdf.pages[0].search(STATEMENT_DATE_RE)
                if len(matches) > 0:
                    statement_date: str = matches[0]["groups"][0]
                    year = statement_date[-4:]

        return year

    def process_dataframe(self, df: pd.DataFrame, year: str) -> pd.DataFrame:
        """
        Clean amounts, parse dates, and delegate to the “description” enricher.

        Parameters
        ----------
        df : pd.DataFrame
            Raw statement rows.
        year : str
            Calendar year that belongs to every *string* date in `df`.

        Returns
        -------
        pd.DataFrame
            Frame ready for further processing.
        """
        if df.empty:
            return df

        df[Col.AMOUNT] = pd.to_numeric(df[Col.AMOUNT], errors="coerce")

        _parse_dates(df, Col.TRANS_DATE, year)
        _parse_dates(df, Col.POST_DATE, year)

        _clean_text(df, [Col.DESCRIPTION, Col.CATEGORY])

        return self.process_dataframe_description(df)

    def process_dataframe_description(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add **province**, **city**, and **store_name** columns.

        The rules are the same as in the original implementation but executed
        in a single vectorised step for readability and speed.
        """
        if df.empty:
            return df

        descr = df[Col.DESCRIPTION].astype(str).str.strip()

        has_at = descr.str.contains("@", na=False)
        is_refund = df[Col.AMOUNT] < 0.0
        is_prime = descr.str.contains("Prime Member", na=False)

        prov_extracted = descr.str[-2:]
        province = np.where(
            has_at | is_refund | is_prime,
            UNKNOWN,
            np.where(prov_extracted.isin(PROVINCES), prov_extracted, UNKNOWN),
        )

        second_last_token = descr.str.split().str[-2]
        token_is_word = second_last_token.str.match(ASCII_WORD_RE, na=False)

        city = np.where(
            province != UNKNOWN,
            np.where(token_is_word, second_last_token, UNKNOWN),
            UNKNOWN,
        )

        store_name_base = descr.str.extract(STORE_NAME_RE, expand=False).str.strip()
        store_name = np.select(
            [has_at, is_refund],
            [store_name_base, UNKNOWN],
            default=store_name_base,
        )

        df[[Col.PROVINCE, Col.CITY, Col.STORE_NAME]] = pd.DataFrame(
            {
                Col.PROVINCE: province,
                Col.CITY: city,
                Col.STORE_NAME: store_name,
            },
            index=df.index,
        )

        return df


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_dates(df: pd.DataFrame, col: str, year_str: str) -> None:
    """
    In-place: `"Jan 1"` + `" 2024"`  →  `pd.Timestamp("2024-01-01")`
    """
    df[col] = pd.to_datetime(
        df[col] + " " + year_str,
        format="%b %d %Y",
        errors="coerce",
    )


def _clean_text(df: pd.DataFrame, columns: list[str]) -> None:
    """Strip leading/trailing whitespace from every column in *columns*."""
    for col in columns:
        df[col] = df[col].astype(str).str.strip()
