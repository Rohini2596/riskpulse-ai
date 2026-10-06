import json
from pathlib import Path

from src.ingestion.loader import load_all_sources
from src.nlp.engine import RiskNlpEngine


PROJECT_FOLDER = Path(__file__).resolve().parent


def main():
    source_files = {
        "news": PROJECT_FOLDER / "data" / "news_sample.csv",
        "social": PROJECT_FOLDER / "data" / "social_sample.csv",
    }

    records = load_all_sources(source_files)
    nlp_engine = RiskNlpEngine()

    output = []
    for record in records:
        signal = nlp_engine.analyze(
            record["text"],
            source=record["source"],
        )
        output.append({
            "record_id": record["record_id"],
            **signal.to_dict(),
        })

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()