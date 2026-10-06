# RiskPulse AI

RiskPulse AI analyzes financial text and demonstrates how an event signal can flow into a synthetic portfolio stress test.

## Current prototype

- **Sentiment:** ProsusAI FinBERT returns a score from -1 to +1.
- **Entity, event, impact, and heuristic confidence:** keyword-based rules.
- **Risk propagation:** event assumptions in `data/scenario_rules.yaml`, scaled by signal impact, confidence, and sentiment.
- **Stress testing:** illustrative repricing of a synthetic portfolio.
- **Dashboard:** Streamlit risk feed, impact-confidence chart, stress results, loss attribution, and transaction dataset summary.

This is a hackathon prototype. Its outputs are scenario estimates, not forecasts or investment advice.

## Run locally

Use Python 3.13 or a compatible Python version.

```powershell
python -m pip install -r requirements.txt
python -m streamlit run dashboard/app.py