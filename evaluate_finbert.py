from collections import Counter, defaultdict
from pathlib import Path

from transformers import pipeline


PROJECT_FOLDER = Path(__file__).resolve().parent
DATA_PATH = PROJECT_FOLDER / "data" / "financial_phrasebank_all_agree.txt"
MODEL_NAME = "ProsusAI/finbert"

LABELS = ["negative", "neutral", "positive"]


def main():
    print(f"Loading {MODEL_NAME}. The first run downloads the model.")
    classifier = pipeline(
        "text-classification",
        model=MODEL_NAME,
        tokenizer=MODEL_NAME,
        device=-1,  # CPU, so this works without a compatible GPU.
    )

    examples = []
    with DATA_PATH.open(encoding="cp1252") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                text, label = line.rsplit("@", maxsplit=1)
            except ValueError as error:
                raise ValueError(
                    f"Line {line_number} is not sentence@label format"
                ) from error

            label = label.strip().lower()
            if label not in LABELS:
                raise ValueError(f"Unknown label on line {line_number}: {label}")

            examples.append((text.strip(), label))

    confusion = defaultdict(Counter)
    correct = 0

    texts = [text for text, _ in examples]
    predictions = classifier(
        texts,
        batch_size=16,
        truncation=True,
    )

    for (_, true_label), prediction in zip(examples, predictions):
        predicted_label = prediction["label"].lower()
        confusion[true_label][predicted_label] += 1
        correct += predicted_label == true_label

    total = len(examples)
    print(f"\nModel: {MODEL_NAME}")
    print(f"Examples evaluated: {total}")
    print(f"Accuracy: {correct / total:.3f}")
    print("\nConfusion matrix (rows=true, columns=predicted):")
    print("true\\pred  " + "  ".join(f"{label:>9}" for label in LABELS))
    for true_label in LABELS:
        counts = "  ".join(
            f"{confusion[true_label][predicted_label]:9d}"
            for predicted_label in LABELS
        )
        print(f"{true_label:10} {counts}")


if __name__ == "__main__":
    main()