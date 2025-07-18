"""
Main entry point for the CIBC statements parser.

This script processes one or more PDF statement files and combines the results.
"""

import pandas as pd

from pdf_processor import PDFProcessor

if __name__ == "__main__":
    processor = PDFProcessor(
        "<your_credit_card_first_4_digits>",
        "<your_credit_card_last_4_digits>",
    )
    pdfs = [
        "data/<name_if_statement_document_1>.pdf",
        "data/<name_if_statement_document_2>.pdf",
    ]

    parsed_docs: list[pd.DataFrame] = [processor.process_pdf(x) for x in pdfs]

    data = pd.concat(parsed_docs, ignore_index=True)
    year = processor.get_year_from_first_page(pdfs[0])
    data = processor.process_dataframe(data, year)

    # for debuging purposes only
    # pd.set_option("display.max_rows", None)
    # print(
    #     data[
    #         [
    #             Col.DESCRIPTION,
    #             Col.CATEGORY,
    #             Col.AMOUNT,
    #             Col.CITY,
    #             Col.PROVINCE,
    #             Col.STORE_NAME,
    #         ]
    #     ]
    # )
    # mask = data[Col.PROVINCE].isna()
    # print(data.loc[mask, [Col.DESCRIPTION, Col.CITY, Col.STORE_NAME]])
