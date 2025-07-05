import pandas as pd
import pdfplumber
from table_extractor import TableExtractor

class PDFProcessor:
    def __init__(self, card_first_four: str, card_last_four: str):
        self.extractor = TableExtractor(card_first_four, card_last_four)

    def process_pdf(self, pdf_path: str) -> pd.DataFrame:
        frames: list[pd.DataFrame] = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages[1:]:
                df = self.extractor.extract_table_data(page)
                frames.append(df)

        full_df = pd.concat(frames, ignore_index=True)

        print(full_df)
        return full_df