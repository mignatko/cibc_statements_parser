"""
Main entry point for the CIBC statements parser.

This script processes one or more PDF statement files and combines the results.
"""

import pandas as pd

from cli_args_parser import CLIArgs
from pdf_processor import PDFProcessor

if __name__ == "__main__":
    args = CLIArgs.from_argv()

    processor = PDFProcessor(
        args.card_first_digits,
        args.card_last_digits,
    )

    parsed_docs: list[pd.DataFrame] = [processor.process_pdf(x) for x in args.docs]

    data = pd.concat(parsed_docs, ignore_index=True)
    year = processor.get_year_from_first_page(args.docs[0])
    data = processor.process_dataframe(
        data,
        year if year is not None else args.default_year,
    )

    # TODO @mignatko: import to csv
