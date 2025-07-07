from pdf_processor import PDFProcessor
import pandas as pd

if __name__ == "__main__":
    processor = PDFProcessor(
        "<your_credit_card_first_4_digits>", "<your_credit_card_last_4_digits>"
    )
    pdfs = [
        "data/<name_if_statement_document_1>.pdf",
        "data/<name_if_statement_document_2>.pdf",
    ]
    parsed_docs: list[pd.DataFrame] = []
    for pdf_path in pdfs:
        parsed_docs.append(processor.process_pdf(pdf_path))

    data = pd.concat(parsed_docs, ignore_index=True)

    # for debuging purposes only
    pd.set_option("display.max_rows", None)
    print(data)
