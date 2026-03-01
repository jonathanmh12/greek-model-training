import argparse
import csv

from sentence_transformers import InputExample, SentenceTransformer, losses
from torch.utils.data import DataLoader


def read_pairs(path: str):
    examples = []
    with open(path, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            sentence1 = row["sentence1"].strip()
            sentence2 = row["sentence2"].strip()
            if sentence1 and sentence2:
                examples.append(InputExample(texts=[sentence1, sentence2]))
    return examples


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-model", required=True)
    parser.add_argument("--train-tsv", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--epochs", type=int, default=4)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=2e-5)
    args = parser.parse_args()

    model = SentenceTransformer(args.base_model)
    train_examples = read_pairs(args.train_tsv)
    if not train_examples:
        raise ValueError("No training examples found in --train-tsv.")

    train_loader = DataLoader(train_examples, shuffle=True, batch_size=args.batch_size)
    train_loss = losses.MultipleNegativesRankingLoss(model)
    warmup_steps = int(len(train_loader) * args.epochs * 0.1)

    model.fit(
        train_objectives=[(train_loader, train_loss)],
        epochs=args.epochs,
        warmup_steps=warmup_steps,
        optimizer_params={"lr": args.lr},
        output_path=args.output_dir,
        show_progress_bar=True,
    )


if __name__ == "__main__":
    main()
