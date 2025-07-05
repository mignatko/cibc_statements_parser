from pdf_processor import PDFProcessor

if __name__ == "__main__":
    processor = PDFProcessor("<your_credit_card_first_4_digits>", "<your_credit_card_last_4_digits>")
    processor.process_pdf("data/<name_if_statement_document>.pdf")