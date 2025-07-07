import pandas as pd
import pdfplumber
from table_extractor import TableExtractor


class PDFProcessor:
    """
    Responsible for processing a whole PDF file for getting statements data from one or more pages
    """

    def __init__(self, card_first_four: str, card_last_four: str):
        self.extractor = TableExtractor(card_first_four, card_last_four)

    def process_pdf(self, pdf_path: str) -> pd.DataFrame:
        """
        Process the PDF file and extract statements data.
        """

        frames: list[pd.DataFrame] = []
        from_page: int = 1  # statements data usually starts from page 2 (index 1)
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[from_page:]:
                df = self.extractor.extract_table_data(page)
                frames.append(df)

        full_df = pd.concat(frames, ignore_index=True)

        return full_df
