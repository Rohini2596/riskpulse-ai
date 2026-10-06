from collections import Counter, defaultdict
from pathlib import Path

from src.nlp.engine import RiskNlpEngine


PROJECT_FOLDER = Path(__file__).resolve().parent
DATA_PATH = PROJECT_FOLDER / "data" / "financial_phrasebank_all_agree.txt"

LABEL_TO_SCORE = {
    "negative": -1.0,
    "neutral": 0.0,
    "positive": 1.0,
}

SCORE_TO_LABEL = {
    -1.0: "negative",
    0.0: "neutral",
    1.0: "positive",
}


def main():
    engine = RiskNlpEngine()
    confusion = defaultdict(Counter)
    correct = 0
    total = 0

    with DATA_PATH.open(encoding="cp1252") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                text, true_label = line.rsplit("@", maxsplit=1)
            except ValueError:
                raise ValueError(
                    f"Line {line_number} is not in sentence@label format"
                )

            true_label = true_label.strip().lower()
            if true_label not in LABEL_TO_SCORE:
                raise ValueError(
                    f"Unknown label on line {line_number}: {true_label}"
                )

            predicted_score = engine._sentiment(text.lower())
            predicted_label = SCORE_TO_LABEL[predicted_score]

            confusion[true_label][predicted_label] += 1
            correct += predicted_label == true_label
            total += 1

    print(f"Examples evaluated: {total}")
    print(f"Accuracy: {correct / total:.3f}")
    print("\nConfusion matrix (rows=true, columns=predicted):")
    labels = ["negative", "neutral", "positive"]
    print("true\\pred  " + "  ".join(f"{label:>9}" for label in labels))
    for true_label in labels:
        counts = "  ".join(
            f"{confusion[true_label][predicted_label]:9d}"
            for predicted_label in labels
        )
        print(f"{true_label:10} {counts}")


if __name__ == "__main__":
    main()