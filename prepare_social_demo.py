import csv
import random
from collections import defaultdict
from pathlib import Path


PROJECT_FOLDER = Path(__file__).resolve().parent
INPUT_PATH = (
    PROJECT_FOLDER / "data" / "twitter_financial_sentiment_valid.csv"
)
OUTPUT_PATH = PROJECT_FOLDER / "data" / "social_sample.csv"

LABEL_NAMES = {
    "0": "bearish",
    "1": "bullish",
    "2": "neutral",
}

groups = defaultdict(list)

with INPUT_PATH.open(encoding="utf-8-sig", newline="") as file:
    for row in csv.DictReader(file):
        label = row["label"].strip()
        text = row["text"].strip()

        if label in LABEL_NAMES and text:
            groups[label].append(text)

rng = random.Random(42)
selected = []

for label in ("0", "1", "2"):
    if len(groups[label]) < 4:
        raise ValueError(f"Not enough examples for label {LABEL_NAMES[label]}")
    for text in rng.sample(groups[label], 4):
        selected.append(text)

rng.shuffle(selected)

with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=["source", "text"])
    writer.writeheader()
    for text in selected:
        writer.writerow({
            "source": "historical-twitter-dataset",
            "text": text,
        })

print(f"Created {len(selected)} demo social posts: {OUTPUT_PATH}")
print("Selected 4 bearish, 4 bullish, and 4 neutral examples.")