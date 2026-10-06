# RiskPulse Data Sources

## SFinDSet transaction data

- File: `SFinDSet.csv`
- Size: 1,048,575 transaction records
- Fields include transaction amount, mode, type, date, and source/destination account identifiers.
- Used for transaction activity counts and date-range charts in the dashboard.
- Amounts are not treated as portfolio asset values. The records describe flows, not loan or security balances.
- Account names and identifiers are not shown in the dashboard.

## News and social demo samples

- `news_sample.csv` contains manually prepared news examples.
- `social_sample.csv` contains 12 text examples sampled from the validation split of the MIT-licensed Twitter Financial News dataset: four each labeled bearish, bullish, and neutral in the source dataset.
- The sentiment labels were removed from the demo CSV; RiskPulse analyzes the text itself.
- These are historical examples for Demo mode, not a live social feed.
- The original validation file is kept out of the public repository.

## Synthetic portfolio

- File: `portfolio.csv`
- Contains assumed holdings totaling $90 million in cash assets, plus a derivative with $10 million notional.
- These holdings are synthetic and are not inferred from SFinDSet transaction amounts.
- Stress results are illustrative scenario calculations, not forecasts or investment advice.

## Current limitations

- Live news and social ingestion are not connected yet.
- The current sentiment, event, confidence, and impact logic uses transparent keyword rules.
- Loan, bond, and derivative repricing use simplified assumptions documented in the project README.