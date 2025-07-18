"""
Main entry point for the CIBC statements parser.

This script processes PDF statement file
with one or multiple statement tables and combines the results.
"""

import pandas as pd
import pdfplumber

from table_extractor import TableExtractor
from table_headers import Col


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

    def process_dataframe(self, df: pd.DataFrame, year: int) -> pd.DataFrame:
        """
        Process a DataFrame containing statement data.

        Args:
            df (pd.DataFrame): DataFrame to process.

        Returns:
            pd.DataFrame: Processed DataFrame with date columns converted.
        """
        if df.empty:
            return df

        df[Col.TRANS_DATE] = pd.to_datetime(
            (df[Col.TRANS_DATE] + " " + year),
            format="%b %d %Y",
        )
        df[Col.POST_DATE] = pd.to_datetime(
            (df[Col.POST_DATE] + " " + year),
            format="%b %d %Y",
        )

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

        # Parse Store name from Description column
        # based on the first word or all before #,* or all before digits
        df[Col.STORE_NAME] = (
            df[Col.DESCRIPTION].str.strip().str.extract(r"^([^\d#,*,/]+)")
        )

        # Parse Province Description last word matches to any of Canada provinces
        provinces = [
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
        ]
        df[Col.PROVINCE] = df[Col.DESCRIPTION].str.extract(
            r"(\b(?:{})\b)".format("|".join(provinces)),
        )

        # Remove leading and trailing whitespace from Description
        mask = (
            df[Col.PROVINCE].notna()
            & ~df[Col.DESCRIPTION].str.contains("@", na=False)
            & df[Col.DESCRIPTION]
            > 0.0
        )

        df.loc[mask, Col.CITY] = (
            df.loc[mask, Col.DESCRIPTION]
            .str.split(" ")
            .str[-3]  # take the 3rd word from the end
        )

        return df
