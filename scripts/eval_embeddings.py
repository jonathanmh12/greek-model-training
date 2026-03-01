import argparse
import csv

import numpy as np
from scipy.stats import pearsonr, spearmanr
from sentence_transformers import SentenceTransformer


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    denom = (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    if denom == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / denom)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--eval-tsv", required=True)
    args = parser.parse_args()

    model = SentenceTransformer(args.model_dir)

    gold = []
    pred = []
    with open(args.eval_tsv, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            sentence1 = row["sentence1"].strip()
            sentence2 = row["sentence2"].strip()
            if not sentence1 or not sentence2:
                continue
            label_text = row.get("label", "").strip()
            if label_text == "":
                continue

            vector1 = model.encode(sentence1, convert_to_numpy=True)
            vector2 = model.encode(sentence2, convert_to_numpy=True)
            score = cosine_similarity(vector1, vector2)

            pred.append(score)
            gold.append(float(label_text))

    if len(gold) < 2:
        raise ValueError("Need at least two labeled rows in --eval-tsv to compute correlations.")

    spearman = spearmanr(gold, pred)
    pearson = pearsonr(gold, pred)

    print(f"rows={len(gold)}")
    print(f"spearman={spearman.statistic:.6f}")
    print(f"pearson={pearson.statistic:.6f}")


if __name__ == "__main__":
    main()
