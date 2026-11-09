"""Create a versioned-dataset demo file.

Writes the first N rows of scikit-learn's breast-cancer dataset to
data/raw/train.csv. Running it with different N simulates a dataset that
grows over time, so each run produces a new "version" for DVC to track.

Usage:
    python make_data.py 300     # dataset v1 (300 rows)
    python make_data.py 569     # dataset v2 (full dataset, 569 rows)
"""
import argparse
import os

from sklearn.datasets import load_breast_cancer

MAX_ROWS = 569


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("rows", type=int, help=f"number of rows to write (1-{MAX_ROWS})")
    parser.add_argument("--out", default="data/raw/train.csv", help="output CSV path")
    args = parser.parse_args()

    if not 1 <= args.rows <= MAX_ROWS:
        parser.error(f"rows must be between 1 and {MAX_ROWS}")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df = load_breast_cancer(as_frame=True).frame
    df.head(args.rows).to_csv(args.out, index=False)
    print(f"Wrote {args.rows} rows to {args.out}")


if __name__ == "__main__":
    main()
