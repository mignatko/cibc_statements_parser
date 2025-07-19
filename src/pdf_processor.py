"""
Main entry point for the CIBC statements parser.

This script processes PDF statement file
with one or multiple statement tables and combines the results.
"""

import numpy as np
import pandas as pd
import pdfplumber

from table_extractor import TableExtractor
from table_headers import Col

UNKNOWN = "UNKNOWN"


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
                matches = pdf.pages[0].search(r"Statement\s+Date\s*([\s\S]+?)\n")
                if len(matches) > 0:
                    statement_date: str = matches[0]["groups"][0]
                    year = statement_date[-4:]

        return year

    def process_dataframe(self, df: pd.DataFrame, year: str) -> pd.DataFrame:
        """
        Process a DataFrame containing statement data.

        Args:
            df (pd.DataFrame): DataFrame to process.

        Returns:
            pd.DataFrame: Processed DataFrame with date columns converted.
        """
        if df.empty:
            return df

        df[Col.AMOUNT] = pd.to_numeric(df[Col.AMOUNT], errors="coerce")

        df[Col.TRANS_DATE] = pd.to_datetime(
            (df[Col.TRANS_DATE] + " " + year),
            format="%b %d %Y",
        )
        df[Col.POST_DATE] = pd.to_datetime(
            (df[Col.POST_DATE] + " " + year),
            format="%b %d %Y",
        )

        for col in [Col.DESCRIPTION, Col.CATEGORY]:
            df[col] = df[col].astype(str).str.strip()

        return self.process_dataframe_description(df)

    def process_dataframe_description(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process the Description column in the DataFrame.

        Args:
            df (pd.DataFrame): DataFrame to process.

        Returns:
            pd.DataFrame: DataFrame with processed Description column.
        """
        if df.empty:
            return df

        # Parse Province Description last word matches to any of Canada provinces
        provinces: set[str] = {
            "AB",
            "BC",
            "MB",
            "NB",
            "NL",
            "NS",
            "NT",
            "NU",
            "ON",
            "PE",
            "QC",
            "SK",
            "YT",
        }

        return (
            df.assign(
                province=lambda d: np.select(
                    [
                        d[Col.DESCRIPTION].str.contains("@", na=False),
                        d[Col.AMOUNT] < 0,
                        d[Col.DESCRIPTION].str.contains("Prime Member", na=False),
                    ],
                    [
                        UNKNOWN,
                        UNKNOWN,
                        UNKNOWN,
                    ],
                    default=d[Col.DESCRIPTION]
                    .str.strip()
                    .str[-2:]
                    .where(lambda s: s.isin(provinces)),
                ),
            )
            .assign(
                city=lambda d: np.select(
                    [
                        ~d[Col.DESCRIPTION]
                        .str.split(" ")
                        .str[-2]
                        .str.fullmatch(r"[A-Za-z]+", na=False),
                        d[Col.PROVINCE] != UNKNOWN,
                        (d[Col.DESCRIPTION].str.strip().str[-3] != " ")
                        & (d[Col.PROVINCE] != UNKNOWN),
                    ],
                    [
                        UNKNOWN,
                        d[Col.DESCRIPTION].str.split(" ").str[-2],
                        UNKNOWN,
                    ],
                    default=UNKNOWN,
                ),
            )
            .assign(
                store_name=lambda d: np.select(
                    [
                        d[Col.DESCRIPTION].str.contains("@", na=False),
                        ~d[Col.DESCRIPTION].str.contains("@", na=False),
                        d[Col.AMOUNT] < 0.0,
                    ],
                    [
                        # TODO @mignatko: add proper handling for next 2 choices
                        d[Col.DESCRIPTION]
                        .str.strip()
                        .str.extract(r"^([^\d#,*,/]+)", expand=False)
                        .str.strip(),
                        d[Col.DESCRIPTION]
                        .str.strip()
                        .str.extract(r"^([^\d#,*,/]+)", expand=False)
                        .str.strip(),
                        UNKNOWN,
                    ],
                    default=UNKNOWN,
                ),
            )
        )
