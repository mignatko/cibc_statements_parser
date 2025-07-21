"""Command-line parsing for the CIBC statement-to-CSV tool.

Public API
~~~~~~~~~~
* :class:`CLIArgs` - immutable dataclass that stores *validated* values.
* The *only* constructor is :meth:`CLIArgs.from_argv`.

Everything else is an implementation detail.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from rich import print as rprint


@dataclass(slots=True, frozen=True)
class CLIArgs:
    """Container for validated CLI parameters.

    Attributes
    ----------
    card_first_digits, card_last_digits
        Four leading / trailing digits of the credit-card number.
    docs
        List of PDF paths found via ``--folder`` or ``--files`` (never
        empty, all paths exist, extension *.pdf*).
    out_csv
        Where the merged CSV will be written.
    default_year
        Fallback year string used when a PDF page lacks a statement year.
    """

    card_first_digits: str
    card_last_digits: str
    docs: list[Path]
    out_csv: Path
    default_year: str

    @classmethod
    def from_argv(cls, argv: list[str] | None = None) -> CLIArgs:
        """Parse *argv* (or :pydata:`sys.argv[1:]`) and return a
        :class:`CLIArgs` instance.

        Parameters
        ----------
        argv
            Sequence of CLI tokens excluding the program name.
            Pass ``None`` in production; tests supply their own list.

        Raises
        ------
        SystemExit
            *Exit code 2* - when :pyclass:`argparse.ArgumentParser`
            rejects the syntax.
            *Exit code 1* - custom validation failures in
            :func:`_expand_docs`.
        """
        ns = _build_parser().parse_args(argv)
        docs = _expand_docs(ns.folder, ns.files)
        return cls(
            card_first_digits=ns.first_digits,
            card_last_digits=ns.last_digits,
            docs=docs,
            out_csv=ns.out,
            default_year=ns.default_year,
        )


# --------------------------------------------------------------------- #
# Private helpers                                                       #
# --------------------------------------------------------------------- #
def _build_parser() -> argparse.ArgumentParser:
    """Return a ready-configured instance of :class:`~argparse.ArgumentParser`."""
    parser = argparse.ArgumentParser(
        prog="cibc-pdf-parser",
        description="Merge CIBC statement PDFs into a single CSV file.",
    )

    parser.add_argument("--first-digits", "-fd", required=True, metavar="1234")
    parser.add_argument("--last-digits", "-ld", required=True, metavar="5678")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--folder",
        type=Path,
        help="Directory with PDFs (non-recursive)",
    )
    group.add_argument(
        "--files",
        nargs="+",
        type=Path,
        metavar="PDF",
        help="Explicit PDF paths",
    )

    parser.add_argument(
        "-o",
        "--out",
        type=Path,
        default=Path("statements_data.csv"),
        metavar="CSV",
        help="Output filename (default: statements_data.csv)",
    )

    parser.add_argument(
        "-y",
        "--default_year",
        default="2000",
        metavar="YYYY",
        help="Year used when a statement date lacks a year (default: 2000)",
    )
    return parser


def _expand_docs(folder: Path | None, files: list[Path] | None) -> list[Path]:
    """Validate folder/files arguments and return a non-empty list of PDFs.

    * Ensures a folder exists and gathers ``*.pdf`` (non-recursive).
    * Ensures every path in *files* exists and has ``.pdf`` suffix.
    * Exits with code 1 on any error.
    """
    docs: list[Path] = []

    # -- folder mode ----------------------------------------------------
    if folder is not None:
        if not folder.is_dir():
            rprint(f"[red]❌ {folder} is not a directory[/red]")
            raise SystemExit(1)
        docs.extend(sorted(folder.glob("*.pdf")))

    # -- explicit files mode -------------------------------------------
    if files:
        for p in files:
            if not (p.is_file() and p.suffix.lower() == ".pdf"):
                rprint(f"[red]❌ {p} is not a .pdf file[/red]")
                raise SystemExit(1)
            docs.append(p)

    # -- no files provided ---------------------------------------------
    if not docs:
        rprint("[red]❌ No PDF files found[/red]")
        raise SystemExit(1)

    return docs
