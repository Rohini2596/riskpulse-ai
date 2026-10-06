import sys
from pathlib import Path
import json
import streamlit as st

PROJECT_FOLDER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_FOLDER))

from src.ingestion.loader import fetch_gdelt_news, load_all_sources
from src.nlp.engine import RiskNlpEngine
from src.risk_propagation.engine import (
    RiskPropagationEngine,
    RiskSignal as PropagationSignal,
)
from src.stress_testing.engine import StressTestEngine


st.set_page_config(
    page_title="RiskPulse AI",
    page_icon="📡",
    layout="wide",
)

st.title("📡 RiskPulse AI")
st.caption("AI-powered event risk signals and portfolio stress testing")

source_files = {
    "news": PROJECT_FOLDER / "data" / "news_sample.csv",
    "social": PROJECT_FOLDER / "data" / "social_sample.csv",
}

mode = st.sidebar.radio("Data mode", ["Demo", "Live"])

if mode == "Live":
    try:
        live_records = fetch_gdelt_news(limit=10)
        social_records = load_all_sources({
            "social": PROJECT_FOLDER / "data" / "social_sample.csv",
        })
        records = live_records + social_records
        st.sidebar.success(f"Loaded {len(live_records)} GDELT headlines.")
    except Exception as error:
        records = load_all_sources(source_files)
        st.sidebar.warning(f"Live news unavailable; using demo data. ({error})")
else:
    records = load_all_sources(source_files)
    st.sidebar.info("Using preloaded demo data.")

nlp_engine = RiskNlpEngine()
propagation_engine = RiskPropagationEngine(
    PROJECT_FOLDER / "data" / "scenario_rules.yaml"
)
stress_engine = StressTestEngine()
portfolio = stress_engine.load_portfolio(
    PROJECT_FOLDER / "data" / "portfolio.csv"
)

results = []

for record in records:
    signal = nlp_engine.analyze(record["text"], source=record["source"])
    propagation_signal = PropagationSignal(
        event=signal.event,
        sentiment=signal.sentiment,
        impact=signal.impact,
        confidence=signal.confidence,
    )
    scenario = propagation_engine.propagate(propagation_signal)

    stress_result = None
    if scenario.action == "STRESS":
        stress_result = stress_engine.run(portfolio, scenario)

    results.append((record, signal, scenario, stress_result))

st.subheader("Risk Feed")
feed_rows = []
for record, signal, scenario, _ in results:
    feed_rows.append({
        "Source": signal.source,
        "Entity": signal.entity,
        "Event": signal.event,
        "Sentiment": signal.sentiment,
        "Impact": signal.impact,
        "Heuristic Confidence": signal.confidence,
        "Action": scenario.action,
    })

st.dataframe(feed_rows, use_container_width=True, hide_index=True)
st.subheader("Impact × Confidence Matrix")

matrix_rows = []
for _, signal, scenario, _ in results:
    matrix_rows.append({
        "Entity": signal.entity,
        "Event": signal.event,
        "Impact": signal.impact,
        "Heuristic Confidence": signal.confidence,
        "Action": scenario.action,
    })

st.scatter_chart(
    matrix_rows,
    x="Impact",
    y="Heuristic Confidence",
    color="Action",
    size="Impact",
    height=400,
)

st.caption(
    "STRESS: impact ≥ 7 and heuristic confidence ≥ 0.7 · "
    "VERIFY: impact ≥ 7 and heuristic confidence < 0.7 · "
    "MONITOR: impact < 7"
)
st.subheader("Select an event to inspect")
labels = [
    f"{signal.entity} · {signal.event} · {record['text'][:70]}"
    for record, signal, _, _ in results
]
selected_index = st.selectbox(
    "Feed item",
    range(len(labels)),
    format_func=lambda index: labels[index],
)

record, signal, scenario, stress_result = results[selected_index]

st.markdown("### Risk Trace")
st.write(f"**Source:** {signal.source}")
st.write(f"**Text:** {signal.text}")
st.write(f"**Entity:** {signal.entity} → **Event:** {signal.event}")
st.write(f"**Action:** {scenario.action}")
st.json(scenario.risk_factors)

if stress_result:
    st.subheader("Stress Test")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Before", f"${stress_result.before_usd / 1e6:.2f}M")
    col2.metric("After", f"${stress_result.after_usd / 1e6:.2f}M")
    col3.metric("P&L", f"${stress_result.pnl_usd / 1e6:.2f}M")
    col4.metric("P&L %", f"{stress_result.loss_pct:.2f}%")

    st.subheader("Loss Attribution")
    attribution_rows = [
        {"Asset Type": asset_type, "P&L ($)": pnl}
        for asset_type, pnl in stress_result.by_asset_type.items()
    ]
    st.bar_chart(
        {row["Asset Type"]: row["P&L ($)"] for row in attribution_rows}
    )
    st.dataframe(attribution_rows, use_container_width=True, hide_index=True)
else:
    st.info("This item is classified as MONITOR or VERIFY; no stress run is triggered.")


profile_path = PROJECT_FOLDER / "data" / "transaction_profile.json"

st.subheader("Transaction Dataset Overview")

if profile_path.exists():
    with profile_path.open(encoding="utf-8") as file:
        profile = json.load(file)

    col1, col2, col3 = st.columns(3)
    col1.metric("Transactions", f"{profile['row_count']:,}")
    col2.metric("Accounts", f"{profile['unique_accounts']:,}")
    col3.metric(
        "Dataset date range",
        f"{profile['date_start'][:10]} to {profile['date_end'][:10]}",
    )

    st.caption(
        "Aggregate overview of the synthetic SFinDSet transaction dataset. "
        "Transaction amounts are not treated as portfolio asset values."
    )

    st.write("Transaction counts by mode")
    st.bar_chart(profile["transaction_modes"])

    st.write("Transaction counts by currency pair")
    st.bar_chart(profile["transaction_types"])
else:
    st.info("Run `python profile_transactions.py` to generate the transaction profile.")