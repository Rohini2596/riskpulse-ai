import csv
import json
from pathlib import Path

from src.nlp.engine import RiskNlpEngine


PROJECT_FOLDER = Path(__file__).resolve().parent


def main():
    engine = RiskNlpEngine()
    sample_path = PROJECT_FOLDER / "data" / "news_sample.csv"

    with sample_path.open(newline="", encoding="utf-8-sig") as file:
        samples = list(csv.DictReader(file))

    signals = [
        engine.analyze(row["text"], source=row["source"]).to_dict()
        for row in samples
    ]

    print(json.dumps(signals, indent=2))


if __name__ == "__main__":
    main()