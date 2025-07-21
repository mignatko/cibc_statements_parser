"""Unit-tests for CLIArgs parsing & validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.cli_args_parser import CLIArgs


def test_files_mode(tmp_path: Path) -> None:
    p1, p2 = tmp_path / "a.pdf", tmp_path / "b.pdf"
    _make_fake_pdf(p1)
    _make_fake_pdf(p2)

    argv: list[str] = [
        "--first-digits",
        "1111",
        "--last-digits",
        "2222",
        "--files",
        str(p1),
        str(p2),
        "-o",
        str(tmp_path / "out.csv"),
        "-y",
        "1999",
    ]
    args = CLIArgs.from_argv(argv)

    assert args.card_first_digits == "1111"
    assert args.card_last_digits == "2222"
    assert args.docs == [p1, p2]
    assert args.out_csv.name == "out.csv"
    assert args.default_year == "1999"


def test_folder_mode(tmp_path: Path) -> None:
    (tmp_path / "x.pdf").write_bytes(b"%PDF-\n%%EOF\n")
    (tmp_path / "y.pdf").write_bytes(b"%PDF-\n%%EOF\n")

    argv = [
        "--first-digits",
        "0000",
        "--last-digits",
        "9999",
        "--folder",
        str(tmp_path),
    ]
    args = CLIArgs.from_argv(argv)

    expected = sorted((tmp_path / "x.pdf", tmp_path / "y.pdf"))
    assert args.docs == expected


@pytest.mark.parametrize(
    "argv",
    [
        # not a directory
        [
            "--first-digits",
            "1111",
            "--last-digits",
            "2222",
            "--folder",
            "not/exists",
        ],
        # file with wrong suffix
        [
            "--first-digits",
            "1111",
            "--last-digits",
            "2222",
            "--files",
            "notes.txt",
        ],
        # empty folder
        [
            "--first-digits",
            "1111",
            "--last-digits",
            "2222",
            "--folder",
            ".",  # tmp_path injected later
        ],
    ],
)
def test_input_validation_errors(tmp_path: Path, argv: list[str]) -> None:
    # Replace "." placeholder with real empty tmp_path
    argv = [str(tmp_path) if x == "." else x for x in argv]

    with pytest.raises(SystemExit) as exc:
        CLIArgs.from_argv(argv)

    # custom validation exits with code 1
    assert exc.value.code == 1


def _make_fake_pdf(path: Path) -> None:
    """Write a minimal PDF header so path.is_file() == True."""
    path.write_bytes(b"%PDF-1.3\n%%EOF\n")
