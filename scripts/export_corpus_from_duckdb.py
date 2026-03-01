import argparse
import random
from pathlib import Path

from clean_data import build_greek_corpus_from_dbt


def parse_whitelist(value: str | None):
    if not value:
        return None
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-out", required=True)
    parser.add_argument("--val-out", required=True)
    parser.add_argument("--val-ratio", type=float, default=0.05)
    parser.add_argument("--min-chars", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--whitelist", type=str, default=None)
    parser.add_argument("--run-dbt", action="store_true")
    parser.add_argument("--dbt-project-dir", default="dbt")
    parser.add_argument("--db-path", default="data/greek_training.duckdb")
    parser.add_argument("--additional-text-path", default=None)
    args = parser.parse_args()

    if not 0 < args.val_ratio < 1:
        raise ValueError("--val-ratio must be between 0 and 1.")

    whitelist = parse_whitelist(args.whitelist)
    corpus = build_greek_corpus_from_dbt(
        whitelist=whitelist,
        run_dbt=args.run_dbt,
        dbt_project_dir=args.dbt_project_dir,
        db_path=args.db_path,
        additional_text_path=args.additional_text_path,
    )

    texts = [line.strip() for line in corpus if line and len(line.strip()) >= args.min_chars]
    if len(texts) < 2:
        raise ValueError("Not enough text rows after filtering to create train/val split.")

    rng = random.Random(args.seed)
    rng.shuffle(texts)

    n_val = max(1, int(len(texts) * args.val_ratio))
    val_texts = texts[:n_val]
    train_texts = texts[n_val:]

    train_out = Path(args.train_out)
    val_out = Path(args.val_out)
    train_out.parent.mkdir(parents=True, exist_ok=True)
    val_out.parent.mkdir(parents=True, exist_ok=True)

    train_out.write_text("\n".join(train_texts), encoding="utf-8")
    val_out.write_text("\n".join(val_texts), encoding="utf-8")

    print(f"train={len(train_texts)} val={len(val_texts)}")


if __name__ == "__main__":
    main()
