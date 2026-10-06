# RiskPulse AI

RiskPulse AI turns financial news and social posts into event risk signals, then demonstrates how those signals could affect a synthetic portfolio.

> Hackathon prototype: outputs are illustrative scenario estimates, not forecasts or investment advice.

## What it does

- **Sentiment:** ProsusAI FinBERT produces a score from -1 (negative) to +1 (positive).
- **Entity, event, impact, confidence:** keyword-based rules identify these fields. Confidence is a heuristic, not a calibrated model probability.
- **Risk propagation:** YAML scenario assumptions are scaled using event impact, confidence, and sentiment.
- **Stress testing:** applies illustrative shocks to a synthetic portfolio and attributes simulated P&L by asset type.
- **Dashboard:** shows the risk feed, impact-confidence matrix, risk trace, stress results, loss attribution, and an aggregate summary of the SFinDSet transaction dataset.

## Requirements

- Python 3.13, or another version supported by the pinned packages in `requirements.txt`
- Internet access the first time FinBERT is used, to download the model

## Run locally

From the repository root in PowerShell:

```powershell
python -m pip install -r requirements.txt
python -m streamlit run dashboard/app.py
```

The dashboard starts in **Demo** mode with bundled sample news and social posts. **Live** mode attempts to fetch current news; if the provider is unavailable or rate-limited, use Demo mode.

## Data and evaluation

- Small, curated demo examples are stored in `data/news_sample.csv` and `data/social_sample.csv`.
- `data/scenario_rules.yaml` contains the illustrative event-to-risk-factor assumptions.
- The SFinDSet transaction data is used only for an aggregate dataset overview. Its transaction amounts are **not** treated as portfolio asset values.
- Raw datasets and local evaluation files are excluded from Git. See [`data/DATA_SOURCES.md`](data/DATA_SOURCES.md) for source notes and [`docs/evaluation.md`](docs/evaluation.md) for evaluation results and limitations.
- See [`docs/architecture.md`](docs/architecture.md) for the system flow.

## Generate the social demo sample

If you have the ignored validation CSV at `data/twitter_financial_sentiment_valid.csv`, you can regenerate the curated social sample:

```powershell
python prepare_social_demo.py
```

The output is a small static historical sample, not a live social-media feed.

## Limitations

- Entity, event, impact, and confidence detection use transparent rules and can misclassify ambiguous text.
- Historical dataset performance does not guarantee performance on live posts or future events.
- Scenario shocks and the synthetic portfolio are for demonstration only.
- GDELT or other live sources may be unavailable or rate-limited; Demo mode is provided for reliable presentations.