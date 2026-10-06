# RiskPulse Data Sources

## SFinDSet transaction data

- File: `SFinDSet.csv`
- Size: 1,048,575 transaction records
- Fields include transaction amount, mode, type, date, and source/destination account identifiers.
- Used for transaction activity counts and date-range charts in the dashboard.
- Amounts are not treated as portfolio asset values. The records describe flows, not loan or security balances.
- Account names and identifiers are not shown in the dashboard.

## News and social demo samples

- Files: `news_sample.csv` and `social_sample.csv`
- These are manually prepared demo examples, not live feeds or a labeled training dataset.
- They demonstrate that the pipeline can process records tagged as news and social.
- The labels produced by the current NLP engine are rule-based prototype outputs.

## Synthetic portfolio

- File: `portfolio.csv`
- Contains assumed holdings totaling $90 million in cash assets, plus a derivative with $10 million notional.
- These holdings are synthetic and are not inferred from SFinDSet transaction amounts.
- Stress results are illustrative scenario calculations, not forecasts or investment advice.

## Current limitations

- Live news and social ingestion are not connected yet.
- The current sentiment, event, confidence, and impact logic uses transparent keyword rules.
- Loan, bond, and derivative repricing use simplified assumptions documented in the project README.