# RiskPulse AI Architecture

```mermaid
flowchart TD
    subgraph Sources
        News[Demo news CSV]
        Social[Demo social CSV]
        GDELT[GDELT headlines<br/>Live mode, may be rate-limited]
        SFinDSet[SFinDSet transaction dataset<br/>Aggregate dashboard profile only]
    end

    News --> Ingest[Load, clean, deduplicate]
    Social --> Ingest
    GDELT --> Ingest

    Ingest --> NLP[Risk NLP engine]
    NLP --> Sentiment[FinBERT sentiment score]
    NLP --> Rules[Rule-based entity, event,<br/>impact, heuristic confidence]
    Sentiment --> Signal[Structured risk signal]
    Rules --> Signal

    Signal --> Propagation[Risk propagation engine]
    YAML[Scenario rules YAML] --> Propagation
    Propagation --> Shocks[Scaled financial risk factors]

    Portfolio[Synthetic portfolio CSV] --> Stress[Stress test engine]
    Shocks --> Stress
    Stress --> Results[Before value, after value,<br/>P&L and attribution]

    Signal --> Dashboard[Streamlit dashboard]
    Results --> Dashboard
    Profile[Aggregated SFinDSet profile JSON] --> Dashboard
```

## Data boundary

SFinDSet is used for aggregate transaction counts and date-range context in the dashboard. Its transaction amounts are not treated as portfolio holdings. The portfolio in `data/portfolio.csv` is synthetic.