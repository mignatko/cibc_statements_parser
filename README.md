# CIBC-Statements Parser

Convert **CIBC credit-card e-statements (PDF)** into one tidy **CSV**
ready for Excel, Pandas, or Power BI.

[![python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#)
[![license](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## ✨ Features

| What it does | Notes |
|--------------|-------|
| **Batch merge** any number of monthly PDFs | `--folder` *or* explicit `--files a.pdf b.pdf …` |
| Reads **transaction/posting dates, amount, category, raw description** | Parsed directly from the PDF table – these columns are correct & reliable |
| *Attempts* to extract **province, city, store name** from the *Description* | Heuristics only – works for many common rows but **not fully complete**. Results may be empty/incorrect, so don’t rely on them for critical analysis (PRs welcome!). |
| Friendly **CLI** with input validation & colourful errors | `argparse` + `rich.print` |
| Typed, formatted, linted, tested | `mypy`, `ruff`, `black`, `pytest`, `pre-commit` |

---

## 🚀 Quick-start

```bash
git clone https://github.com/<you>/cibc-statements-parser.git
cd cibc-statements-parser
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Run the parser on specific files:

```bash
python -m src.main \
  --first-digits 1234 \
  --last-digits 5678 \
  --files data/May.pdf data/Jun.pdf \
  -o merged.csv
  -y 2025
```
## Run the parser on every PDF in a folder (without nested folders):

```bash
python -m src.main \
  --first-digits 1234 \
  --last-digits 5678 \
  --folder data/ \
  -o merged.csv
  -y 2025
```

---

## 🤝 Contributing

1. **Fork** the repo & create a feature branch.  
2. Implement your improvement (especially better province / city / store parsing).
3.	Ensure `pre-commit run --all-files` and `pytest -q` are green.
4.	Open a pull request — thank you!

---

## 📄 License

Distributed under the **MIT License** – see [`LICENSE`](LICENSE).

> **Disclaimer:** This tool is **NOT** affiliated with CIBC.  
> Always use responsibly, and never commit private or sensitive data  
> (e.g. real card numbers or PDF statements).