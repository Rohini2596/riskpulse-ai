import csv
from collections import Counter, defaultdict
from pathlib import Path

from transformers import pipeline

from src.nlp.engine import RiskNlpEngine


PROJECT_FOLDER = Path(__file__).resolve().parent
DATA_PATH = (
    PROJECT_FOLDER
    / "data"
    / "twitter_financial_sentiment_valid.csv"
)

LABELS = ["negative", "neutral", "positive"]
DATASET_LABELS = {
    "0": "negative",  # bearish
    "1": "positive",  # bullish
    "2": "neutral",
}


def print_metrics(name, true_labels, predicted_labels):
    confusion = defaultdict(Counter)
    correct = 0

    for true_label, predicted_label in zip(true_labels, predicted_labels):
        confusion[true_label][predicted_label] += 1
        correct += true_label == predicted_label

    total = len(true_labels)
    print(f"\n{name}")
    print(f"Accuracy: {correct / total:.3f}")
    print("Confusion matrix (rows=true, columns=predicted):")
    print("true\\pred  " + "  ".join(f"{label:>9}" for label in LABELS))

    for true_label in LABELS:
        counts = "  ".join(
            f"{confusion[true_label][predicted_label]:9d}"
            for predicted_label in LABELS
        )
        print(f"{true_label:10} {counts}")


def main():
    texts = []
    true_labels = []

    with DATA_PATH.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            text = row["text"].strip()
            label = DATASET_LABELS[row["label"].strip()]

            if text:
                texts.append(text)
                true_labels.append(label)

    print(f"Validation posts: {len(texts)}")

    keyword_engine = RiskNlpEngine()
    keyword_predictions = []

    for text in texts:
        score = keyword_engine._sentiment(text.lower())
        if score < 0:
            keyword_predictions.append("negative")
        elif score > 0:
            keyword_predictions.append("positive")
        else:
            keyword_predictions.append("neutral")

    print_metrics("Keyword baseline", true_labels, keyword_predictions)

    classifier = pipeline(
        "text-classification",
        model="ProsusAI/finbert",
        tokenizer="ProsusAI/finbert",
        device=-1,
    )

    model_predictions = []
    outputs = classifier(texts, batch_size=16, truncation=True)

    for output in outputs:
        label = output["label"].lower()

        # Some model configs return LABEL_0-style names.
        if label.startswith("label_"):
            label = classifier.model.config.id2label[
                int(label.split("_")[1])
            ].lower()

        model_predictions.append(label)

    print_metrics("ProsusAI FinBERT", true_labels, model_predictions)


if __name__ == "__main__":
    main()